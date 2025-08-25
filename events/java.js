export function register(app) {
  app.message(/java/i, async ({ message, client, say }) => {
    try {
      await client.reactions.add({
        channel: message.channel,
        name: "java",
        timestamp: message.ts
      });

      //java template
      await client.chat.postMessage({
        channel: message.channel,
        thread_ts: message.ts,
        text: "```public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, World!\");\n    }\n}\n```"
      });
    } catch (err) {
      console.error("[java.js] error:", err);
    }
  });
}