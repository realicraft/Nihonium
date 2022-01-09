package src;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map.Entry;
import java.util.Scanner;
import java.util.logging.Logger;

import org.json.JSONObject;

import javax.security.auth.login.LoginException;

import net.dv8tion.jda.api.JDA;
import net.dv8tion.jda.api.JDABuilder;

/**
 * A simple Discord integration of Nihonium. This is the successor of Flerovium,
 * but using JDA instead of discord.py.
 * 
 * @author gilbertdlo
 * @version 2.0.0-alpha
 *
 */

public class Main {
	public static JDA jda;
	public static String token;
	public static LocalDateTime uptime = LocalDateTime.now();
	final static Logger LOGGER = Logger.getLogger(Logger.GLOBAL_LOGGER_NAME);

	// This sets settings for/from the config.json file.
	public static HashMap<String, String> botInfo = new HashMap<String, String>();
	public static HashMap<String, Integer> stats = new HashMap<String, Integer>();

	public static void main(String[] args) throws LoginException, FileNotFoundException, IOException {
		// Initial checks.
		Process proc = Listener.rt.exec("python3");
		proc.destroy();
		loadConfig();
		uptime = LocalDateTime.now();

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
		System.out.println("Flerovium is active.");
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
}
