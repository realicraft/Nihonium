package src;

import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.json.JSONArray;
import org.json.JSONObject;

import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.entities.MessageChannel;
import net.dv8tion.jda.api.entities.User;
import net.dv8tion.jda.api.events.interaction.SlashCommandEvent;
import net.dv8tion.jda.api.events.message.MessageReceivedEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;
import net.dv8tion.jda.api.interactions.InteractionHook;
import net.dv8tion.jda.api.interactions.commands.OptionMapping;
// import java.util.stream.Stream;

/**
 * A command listener.
 * <p>
 * This listens to messages and slash commands, and calls cli.py to
 * process the command.
 * 
 * @author gilbertdlo
 *
 */

public class Listener extends ListenerAdapter {
	Pattern pattern = Pattern.compile("fl!(.+)");
	String phase = "";

	public void interpretResponse(String response, MessageChannel sender) {
		JSONObject obj = new JSONObject(response);
		String type = obj.getString("type");
		if (type.equals("text")) {
			Main.LOGGER.log(Level.FINE, "Received text");
			sender.sendMessage(obj.getString("data")).queue();
		} else if (type.equals("embed")) {
			Main.LOGGER.log(Level.FINE, "Received embed");
			EmbedBuilder embed = new EmbedBuilder();
			JSONArray fields = obj.getJSONArray("fields");
			String title = obj.getString("title");
			embed.setTitle(title);
			for (int i = 0; i < fields.length(); i++) {
				JSONObject f = fields.getJSONObject(i); // why
				embed.addField(f.getString("name"), f.getString("value"), false);
			}
			sender.sendMessageEmbeds(embed.build()).queue();
		}
	}
	
	// this sucks
	public void interpretResponse(String response, InteractionHook sender) {
		JSONObject obj = new JSONObject(response);
		String type = obj.getString("type");
		if (type.equals("text")) {
			Main.LOGGER.log(Level.FINE, "Received text");
			sender.sendMessage(obj.getString("data")).queue();
		} else if (type.equals("embed")) {
			Main.LOGGER.log(Level.FINE, "Received embed");
			EmbedBuilder embed = new EmbedBuilder();
			JSONArray fields = obj.getJSONArray("fields");
			String title = obj.getString("title");
			embed.setTitle(title);
			for (int i = 0; i < fields.length(); i++) {
				JSONObject f = fields.getJSONObject(i); // why
				embed.addField(f.getString("name"), f.getString("value"), false);
			}
			sender.sendMessageEmbeds(embed.build()).queue();
		}
	}
	
	public String getResponse(String name, String discr, String id, String[] args) throws IOException {
		String out;
		try {
			out = Main.callPython("cli.py", name, discr, id, String.join(" ", args));
		} catch (Exception e) {
			String err = e.getMessage();
			String msg = String.format(
					":warning: While interpreting that command, a Python error occured:\n```\n%s\n```",
					err);
			Main.LOGGER.log(Level.SEVERE, msg);
			JSONObject json = new JSONObject();
			json.put("type", "text");
			json.put("data", msg);
			return String.format("%s", json.toString());
		}
		return out;
	}
	
	public String getResponse(String name, String discr, String id, ArrayList<String> args) throws IOException {
		String[] a = new String[args.size()];
		a = args.toArray(a);
		return getResponse(name, discr, id, a);
	}
	
	@SuppressWarnings("unused")
	@Override
	public void onMessageReceived(MessageReceivedEvent event) {
		if (event.getAuthor().isBot())
			return; // don't respond to bots
		MessageChannel channel = event.getChannel();
		Main.LOGGER.log(Level.INFO, String.format("Received message %s from %s", event.getMessage().getContentRaw(),
				event.getAuthor().toString()));
		try {
			phase = "parsing";
			String message = event.getMessage().getContentRaw();
			Matcher match = pattern.matcher(message);
			Main.stats.put("commands_found", Main.stats.get("commands_found") + 1);
			if (match.matches()) {
				// Get stuff
				channel.sendTyping().queue();
				User user = event.getAuthor();
				String name = user.getName();
				String discr = user.getDiscriminator();
				String id = user.getId();

				// Prepare for Python
				phase = "interpreting";
				String[] args = match.group(1).split(" ");
				Main.stats.put("commands_parsed", Main.stats.get("commands_parsed") + 1);
				Main.saveConfig();
				String out = getResponse(name, discr, id, args);
				interpretResponse(out, channel);
				Main.stats.put("valid_commands", Main.stats.get("valid_commands") + 1);
			}
		} catch (Exception e) {
			StringWriter sw = new StringWriter();
			e.printStackTrace(new PrintWriter(sw));
			String ex = sw.toString();
			Main.LOGGER.log(Level.SEVERE,
					String.format(":warning: While %s that command, an error occured:\n```\n%s\n```", phase, ex));
			channel.sendMessage(String.format("While %s that command, an error occured:\n```\n%s\n```", phase, ex))
					.queue();
		}
	}
	
	@SuppressWarnings("unused")
	@Override
	public void onSlashCommand(SlashCommandEvent event) {
		if (event.getUser().isBot())
			return; // don't respond to bots
		InteractionHook hook = event.getHook();
		Main.LOGGER.log(Level.INFO, String.format("Received slash command %s from %s", event.getCommandString(),
				event.getUser().toString()));
		try {
			phase = "parsing";
			Main.stats.put("commands_found", Main.stats.get("commands_found") + 1);
			
			// Get stuff
			event.deferReply().queue();
			User user = event.getUser();
			String name = user.getName();
			String discr = user.getDiscriminator();
			String id = user.getId();

			// Prepare for Python
			phase = "interpreting";
			List<OptionMapping> options = event.getOptions();
			ArrayList<String> args = new ArrayList<String>();
			if (event.getSubcommandName() != null) args.add(event.getSubcommandName());
			else args.add(event.getName());
			for (int i = 0; i < options.size(); i++) {
				switch (options.get(i).getType()){
				case STRING:
				case INTEGER:
				case NUMBER:
					args.add(options.get(i).getAsString());
				default:
					throw new ClassNotFoundException(String.format("Unknown type %s", options.get(i).getType()));
				}
			}
			
			Main.stats.put("commands_parsed", Main.stats.get("commands_parsed") + 1);
			Main.saveConfig();
			
			String out = getResponse(name, discr, id, args);
			interpretResponse(out, hook);
			Main.stats.put("valid_commands", Main.stats.get("valid_commands") + 1);
		} catch (Exception e) {
			StringWriter sw = new StringWriter();
			e.printStackTrace(new PrintWriter(sw));
			String ex = sw.toString();
			Main.LOGGER.log(Level.SEVERE,
					String.format(":warning: While %s that command, an error occured:\n```\n%s\n```", phase, ex));
			event.reply(String.format("While %s that command, an error occured:\n```\n%s\n```", phase, ex))
			.setEphemeral(true).queue();
		}
	}
}
