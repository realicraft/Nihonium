package src;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.HashMap;
import java.util.logging.Level;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.json.JSONArray;
import org.json.JSONObject;

import net.dv8tion.jda.api.EmbedBuilder;
import net.dv8tion.jda.api.entities.MessageChannel;
import net.dv8tion.jda.api.entities.User;
import net.dv8tion.jda.api.events.message.MessageReceivedEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;
// import java.util.stream.Stream;

/**
 * A command listener.
 * <p>
 * This listens to messages (and slashes in the future), and calls cli.py to
 * process the command.
 * 
 * @author gilbertdlo
 *
 */

public class Listener extends ListenerAdapter {
	Pattern pattern = Pattern.compile("fl!(.+)");
	public static Runtime rt = Runtime.getRuntime();
	String phase = "";

	@SuppressWarnings("unused")
	@Override
	public void onMessageReceived(MessageReceivedEvent event) {
		if (event.getAuthor().isBot())
			return;
		MessageChannel channel = event.getChannel();
		Main.LOGGER.log(Level.INFO, String.format("Received message %s from %s", event.getMessage().getContentRaw(),
				event.getAuthor().toString()));
		try {
			phase = "parsing";
			String message = event.getMessage().getContentRaw();
			Matcher match = pattern.matcher(message);
			if (match.matches()) {
				// Get stuff
				channel.sendTyping().queue();
				User user = event.getAuthor();
				String name = user.getName();
				String discr = user.getDiscriminator();
				String id = user.getId();

				// Prepare for Python
				String[] args = match.group(1).split(" ");
				String commands = String.format("python3 cli.py %s %s %s", name, discr, id);
				commands += " " + String.join(" ", args);

				phase = "interpreting";
				Process proc = rt.exec(commands);
				BufferedReader stdout = new BufferedReader(new InputStreamReader(proc.getInputStream())); // get the
																											// output
				BufferedReader stderr = new BufferedReader(new InputStreamReader(proc.getErrorStream())); // get the
																											// error
				String out = stdout.readLine();
				String s = "";
				String err = "";
				while ((s = stderr.readLine()) != null)
					err += s + "\n";
				proc.destroy();

				assert out != null || err != null;
				Main.LOGGER.log(Level.INFO, String.format("Received output %s from Python", out));
				// post the message
				phase = "sending";
				if (err != "") {
					String msg = String.format("While interpreting that command, a Python error occured:\n```\n%s\n```",
							err);
					Main.LOGGER.log(Level.SEVERE, msg);
					channel.sendMessage(msg).queue();
					return;
				} else {
					JSONObject obj = new JSONObject(out);
					String type = obj.getString("type");
					if (type.equals("text")) {
						Main.LOGGER.log(Level.INFO, "Received text");
						channel.sendMessage(obj.getString("data")).queue();
					} else if (type.equals("embed")) {
						Main.LOGGER.log(Level.INFO, "Received embed");
						EmbedBuilder embed = new EmbedBuilder();
						JSONArray fields = obj.getJSONArray("fields");
						String title = obj.getString("title");
						embed.setTitle(title);
						for (int i = 0; i < fields.length(); i++) {
							JSONObject f = fields.getJSONObject(i); // why
							embed.addField(f.getString("name"), f.getString("value"), false);
						}

						channel.sendMessageEmbeds(embed.build()).queue();
					}
				}

			}
		} catch (Exception e) {
			StringWriter sw = new StringWriter();
			e.printStackTrace(new PrintWriter(sw));
			String ex = sw.toString();
			Main.LOGGER.log(Level.SEVERE,
					String.format("While %s that command, an error occured:\n```\n%s\n```", phase, ex));
			channel.sendMessage(String.format("While %s that command, an error occured:\n```\n%s\n```", phase, ex))
					.queue();
		}
	}
}
