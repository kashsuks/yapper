import { withBlacklistCommand } from "./blacklist.js";

const OWNER_ID = process.env.OWNER;
const protectedGroups = new Set();

export function register(app) {
  app.command("/protect-group", async ({ ack, body, client, respond }) => {
    console.log("[pingGroup] /protect-group command received");
    await ack();

    const userId = body.user_id;

    if (userId !== OWNER_ID) {
      await respond({
        text: "Only the bot owner can use this command",
        response_type: "ephemeral"
      });
      return;
    }

    const groupHandle = body.text.trim();

    if (!groupHandle) {
      await respond({
        text: "Please provide a usergroup handle (e.g., `@developers` or just `developers`)",
        response_type: "ephemeral"
      });
      return;
    }

    let cleanHandle;
    const subteamMatch = groupHandle.match(/<!subteam\^([A-Z0-9]+)\|@?(.+?)>/);
    if (subteamMatch) {
      const subteamId = subteamMatch[1];
      console.log(`[pingGroup] Detected subteam ID from mention: ${subteamId}`);
      
      try {
        const result = await client.usergroups.list({
          include_users: false
        });
        
        const group = result.usergroups.find(g => g.id === subteamId);
        
        if (!group) {
          await respond({
            text: `Could not find usergroup with ID: \`${subteamId}\``,
            response_type: "ephemeral"
          });
          return;
        }
        
        protectedGroups.add(group.id);

        await respond({
          text: `Now protecting usergroup \`@${group.handle}\` (ID: ${group.id}) from unauthorized removals.`,
          response_type: "ephemeral"
        });

        console.log(`[pingGroup] Protected group added: ${group.handle} (${group.id})`);
        return;
      } catch (error) {
        console.error("[pingGroup] Error fetching usergroups:", error);
        await respond({
          text: `Error: ${error.message}`,
          response_type: "ephemeral"
        });
        return;
      }
    } else {
      cleanHandle = groupHandle.replace(/^@/, '');
    }

    try {
      const result = await client.usergroups.list({
        include_users: false
      });

      const group = result.usergroups.find(g => g.handle === cleanHandle);

      if (!group) {
        await respond({
          text: `Could not find usergroup with the handle \`${cleanHandle}\``,
          response_type: "ephemeral"
        });
        return;
      }
      
      protectedGroups.add(group.id);

      await respond({
        text: `Now protecting usergroup \`@${group.handle}\` (ID: ${group.id}) from unauthorized removals.`,
        response_type: "ephemeral"
      });
      
      console.log(`[pingGroup] Protected group added: ${group.handle} (${group.id})`);
    } catch (error) {
      console.error("[pingGroup] Error fetching usergroups:", error);
      await respond({
        text: `Error: ${error.message}`,
        response_type: "ephemeral"
      });
    }
  });

  app.command("/unprotect-group", withBlacklistCommand('unprotect-group', async ({ ack, body, client, respond }) => {
    await ack();

    const userId = body.user_id;

    if (userId !== OWNER_ID) {
      await respond({
        text: "Only the bot owner can use this command",
        response_type: "ephemeral"
      });
      return;
    }

    const groupHandle = body.text.trim();

    if (!groupHandle) {
      await respond({
        text: "Please provide a usergroup handle (e.g., `@developers` or just `developers`)",
        response_type: "ephemeral"
      });
      return;
    }

    // parse the group handle - Slack converts @mentions to <!subteam^ID|@handle> format
    let cleanHandle;
    const subteamMatch = groupHandle.match(/<!subteam\^([A-Z0-9]+)\|@?(.+?)>/);
    if (subteamMatch) {
      // if it's in the <!subteam^ID|@handle> format, extract the ID
      const subteamId = subteamMatch[1];
      console.log(`[pingGroup] Detected subteam ID from mention: ${subteamId}`);
      
      try {
        const result = await client.usergroups.list({
          include_users: false
        });
        
        const group = result.usergroups.find(g => g.id === subteamId);
        
        if (!group) {
          await respond({
            text: `Could not find usergroup with ID: \`${subteamId}\``,
            response_type: "ephemeral"
          });
          return;
        }
        
        protectedGroups.delete(group.id);

        await respond({
          text: `No longer protecting usergroup \`@${group.handle}\` (ID: ${group.id})`,
          response_type: "ephemeral"
        });

        console.log(`[pingGroup] Protected group removed: ${group.handle} (${group.id})`);
        return;
      } catch (error) {
        console.error("[pingGroup] Error fetching usergroups:", error);
        await respond({
          text: `Error: ${error.message}`,
          response_type: "ephemeral"
        });
        return;
      }
    } else {
      cleanHandle = groupHandle.replace(/^@/, '');
    }

    try {
      const result = await client.usergroups.list({
        include_users: false
      });

      const group = result.usergroups.find(g => g.handle === cleanHandle);

      if (!group) {
        await respond({
          text: `Could not find usergroup with handle: \`${cleanHandle}\``,
          response_type: "ephemeral"
        });
        return;
      }

      protectedGroups.delete(group.id);

      await respond({
        text: `No longer protecting usergroup \`@${group.handle}\` (ID: ${group.id})`,
        response_type: "ephemeral"
      });

      console.log(`[pingGroup] Protected group removed: ${group.handle} (${group.id})`);
    } catch (error) {
      console.error("[pingGroup] Error fetching usergroups:", error);
      await respond({
        text: `Error: ${error.message}`,
        response_type: "ephemeral"
      });
    }
  }));

  app.command("/list-protected", withBlacklistCommand('list-protected', async ({ ack, body, client, respond }) => {
    await ack();

    const userId = body.user_id;

    if (userId !== OWNER_ID) {
      await respond({
        text: "Only the bot owner can use this command",
        response_type: "ephemeral"
      });
      return;
    }

    if (protectedGroups.size === 0) {
      await respond({
        text: "No usergroups are currently protected",
        response_type: "ephemeral"
      });
      return;
    }

    try {
      const result = await client.usergroups.list({
        include_users: false
      });

      let text = "*Protected Usergroups:*\n";

      for (const groupId of protectedGroups) {
        const group = result.usergroups.find(g => g.id === groupId);
        if (group) {
          text += `• \`@${group.handle}\` (ID: ${groupId})\n`;
        } else {
          text += `• Unknown group (ID: ${groupId})\n`;
        }
      }

      await respond({
        text,
        response_type: "ephemeral"
      });
    } catch (error) {
      console.error("[pingGroup] Error listing protected groups:", error);
      await respond({
        text: `Error: ${error.message}`,
        response_type: "ephemeral"
      });
    }
  }));

  app.event('subteam_members_changed', async ({ event, client }) => {
    try {
      const usergroupId = event.subteam_id;
      
      if (!protectedGroups.has(usergroupId)) {
        return;
      }

      const previousMembers = new Set(event.previous_member_ids || []);
      const currentMembers = new Set(event.member_ids || []);

      const removedUsers = [...previousMembers].filter(user => !currentMembers.has(user));

      if (removedUsers.length === 0) {
        return; // Case when no one was removed and someone was probably added
      }

      const updatedBy = event.subteam_updated_by;

      const groupInfo = await client.usergroups.info({
        usergroup: usergroupId
      });
      const groupHandle = groupInfo.usergroup.handle;

      for (const removedUser of removedUsers) {
        if (removedUser === updatedBy) {
          console.log(`[pingGroup] User ${removedUser} removed themselves from @${groupHandle} - allowing`);
          continue;
        }

        if (updatedBy === OWNER_ID) {
          console.log(`[pingGroup] Owner removed ${removedUser} from @${groupHandle} - allowing`);
          continue;
        }

        console.log(`[pingGroup] User ${updatedBy} tried to remove ${removedUser} from @${groupHandle} - adding back`);

        const updatedMembers = [...currentMembers, removedUser];

        await client.usergroups.users.update({
          usergroup: usergroupId,
          users: updatedMembers.join(',')
        });

        try {
          await client.chat.postMessage({
            channel: updatedBy,
            text: `You cannot remove <@${removedUser}> from \`@${groupHandle}\`. Only they can remove themselves or the bot owner can remove them.`
          });
        } catch (dmError) {
          console.error(`[pingGroup] Could not send DM to ${updatedBy}:`, dmError);
        }

        console.log(`[pingGroup] Successfully restored ${removedUser} to @${groupHandle}`);
      }
    } catch (error) {
      console.error('[pingGroup] Error handling subteam_members_changed:', error);
    }
  });
}