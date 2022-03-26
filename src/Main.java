package src;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map.Entry;
import java.util.Scanner;
import java.util.logging.FileHandler;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;

import javax.security.auth.login.LoginException;

import org.json.JSONObject;

import net.dv8tion.jda.api.JDA;
import net.dv8tion.jda.api.JDABuilder;
import net.dv8tion.jda.api.interactions.commands.OptionType;
import net.dv8tion.jda.api.interactions.commands.build.CommandData;
import net.dv8tion.jda.api.interactions.commands.build.SubcommandData;
import net.dv8tion.jda.api.requests.restaction.CommandListUpdateAction;

/**
 * A simple Discord integration of Nihonium. This is the successor of Flerovium,
 * but using JDA instead of discord.py.
 * 
 * @author gilbertdlo
 * @version 2.0.0-alpha-2
 *
 */

public class Main {
	public static JDA jda;
	public static String token;
	
	public static LocalDateTime uptime = LocalDateTime.now();
	final static Logger LOGGER = Logger.getLogger("Flerovium");
	static FileHandler fh;
	
	public static HashSet<Flags> flags = new HashSet<Flags>();
	public static Runtime rt = Runtime.getRuntime();

	// This sets settings for/from the config.json file.
	public static HashMap<String, String> botInfo = new HashMap<String, String>();
	public static HashMap<String, Integer> stats = new HashMap<String, Integer>();

	public enum Flags {
		SETUP_GLOBAL_COMMANDS,
		SETUP_GUILD_COMMANDS,
		USE_SUBCOMMANDS,
		READONLY
	}
	
	public static String callPython(String prog, String... args) throws IOException {
		String commands = String.format("python3 %s %s", prog, String.join(" ", args));
		
		// Call Python
		Process proc = rt.exec(commands);
		BufferedReader stdout = new BufferedReader(new InputStreamReader(proc.getInputStream())); // get the stdout																		// output
		BufferedReader stderr = new BufferedReader(new InputStreamReader(proc.getErrorStream())); // get the stderr
		
		// Get stuff
		String out = "";
		String s = "";
		while ((s = stdout.readLine()) != null)
			out += s + "\n";
		String err = "";
		while ((s = stderr.readLine()) != null)
			err += s + "\n";
		proc.destroy();

		// Checks
		assert out != null || err != null;
		if (err != "") throw new IOException(err);
		return out;
	}
	
	public static void main(String[] args) throws LoginException, FileNotFoundException, IOException {
		// Get arguments.
 		// Like all of my bots, it uses args as a flag marker.
 		for (String s: args) flags.add(Flags.valueOf(s.toUpperCase()));
 		
 		// Set up file logging.
 		if (!flags.contains(Flags.READONLY)) {
			fh = new FileHandler(String.format("logs/java-%s.log", uptime.format(DateTimeFormatter.BASIC_ISO_DATE)), true);  
	        LOGGER.addHandler(fh);
	        SimpleFormatter formatter = new SimpleFormatter();  
	        fh.setFormatter(formatter);  
 		}
 		
		// Initial checks.
		LOGGER.log(Level.INFO, "Flerovium is starting...");
		Process proc = Main.rt.exec("python3");
		proc.destroy();
		loadConfig();
		uptime = LocalDateTime.now();
		stats.put("commands_found", 0);
		stats.put("commands_parsed", 0);
		stats.put("valid_commands", 0);

		// Hello world.
		System.out.println("Flerovium: Java Edition\nA basic Discord intergration of Nihonium.");

		// Get token.
		File tokenFile = new File("token.txt");
		Scanner reader = new Scanner(tokenFile);
		token = reader.nextLine();
		reader.close();

		// Make the entire bot.
		JDA jda = JDABuilder.createDefault(token).build();
		jda.addEventListener(new Listener());
		LOGGER.log(Level.INFO, "Flerovium is active.");
		System.out.println("Flerovium is active.");
		
		// Add commands
		if (flags.contains(Flags.SETUP_GUILD_COMMANDS)) setupCommands(jda.getGuildById(Long.parseLong(System.getenv("GUILD_ID"))).updateCommands());
		// if (flags.contains(Flags.SETUP_GLOBAL_COMMANDS)) setupCommands(jda.updateCommands());
	}

	// @SuppressWarnings("unchecked")
	public static void loadConfig() throws IOException {
		botInfo = new HashMap<String, String>();
		stats = new HashMap<String, Integer>();
		FileReader configFile = new FileReader("config.json");
		BufferedReader reader = new BufferedReader(configFile);
		String config = "";
		for (String s = reader.readLine(); s != null; s = reader.readLine())
			config += s + "\n"; // big brain moment
		reader.close();
		JSONObject json = new JSONObject(config);
		uptime = LocalDateTime.parse(json.getString("uptime"));
		// ew
		for (Entry<String, Object> entry : json.getJSONObject("stats").toMap().entrySet())
			stats.put(entry.getKey(), (Integer) entry.getValue());
		for (Entry<String, Object> entry : json.getJSONObject("bot_info").toMap().entrySet())
			botInfo.put(entry.getKey(), (String) entry.getValue());
	}

	public static void saveConfig() throws IOException {
		JSONObject json = new JSONObject();
		json.put("uptime", uptime.toString());
		json.put("stats", stats);
		json.put("bot_info", botInfo);
		FileWriter configFile = new FileWriter("config.json");
		configFile.write(json.toString(1));
		configFile.close();
	}
	
	/**
	 * Sets up commands.
	 */
	public static void setupCommands(CommandListUpdateAction action) {
		LOGGER.log(Level.INFO, "Adding slash commands...");
		JSONObject json = new JSONObject();
		if (flags.contains(Flags.USE_SUBCOMMANDS)) {
			CommandData command = new CommandData(botInfo.get("id"), "The root of all Flerovium commands.");
			for (Entry<String, Object> entry : json.toMap().entrySet()) {
				JSONObject data = (JSONObject)entry.getValue();
				SubcommandData subcommand = new SubcommandData(entry.getKey(), data.getString("shortDescription"));
				for (Object i: data.getJSONArray("inputs").toList()) {
					JSONObject input = (JSONObject) i;
					OptionType option;
					switch (input.getString("type")) {
					case "int":
						option = OptionType.INTEGER;
					case "float":
						option = OptionType.NUMBER;
					case "str":
					default:
						option = OptionType.STRING;
					}
					subcommand.addOption(option, input.getString("name"), input.getString("description"));
				}
				command.addSubcommands(subcommand);
			}
			action.addCommands(command);
		} else {
			for (Entry<String, Object> entry : json.toMap().entrySet()) {
				JSONObject data = (JSONObject)entry.getValue();
				CommandData command = new CommandData(entry.getKey(), data.getString("shortDescription"));
				for (Object i: data.getJSONArray("inputs").toList()) {
					JSONObject input = (JSONObject) i;
					OptionType option;
					switch (input.getString("type")) {
					case "int":
						option = OptionType.INTEGER;
					case "float":
						option = OptionType.NUMBER;
					case "str":
					default:
						option = OptionType.STRING;
					}
					command.addOption(option, input.getString("name"), input.getString("description"));
				}
				action.addCommands(command);
			}
		}
		action.queue();
	}
}
