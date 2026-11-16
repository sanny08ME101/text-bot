import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# --- CONFIGURATION ---
# Replace with your actual numeric Telegram User ID from @userinfobot
ADMIN_ID = 148295610  
# Replace with your new BotFather token
TOKEN = "YOUR_NEW_BOT_TOKEN_HERE"  

# Store a mapping of message IDs in your admin chat to the user's ID
# format: { admin_chat_reply_message_id: original_user_id }
active_conversations = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message

    if not message:
        return

    # --- IF THE MESSAGE IS FROM YOU (THE ADMIN) ---
    if user.id == ADMIN_ID:
        # Check if you are hitting "Reply" on a forwarded user message
        if message.reply_to_message:
            original_msg_id = message.reply_to_message.message_id
            target_user_id = active_conversations.get(original_msg_id)
            
            if target_user_id:
                try:
                    # Send your response to the user
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text=f"💬 **Admin Reply:**\n\n{message.text or message.caption}"
                    )
                    await message.reply_text("✅ Reply sent successfully!")
                except Exception as e:
                    await message.reply_text(f"❌ Failed to send reply: {e}")
            else:
                await message.reply_text("⚠️ Could not find the user associated with this message. Make sure you reply directly to the forwarded message card.")
        return

    # --- IF THE MESSAGE IS FROM A REGULAR USER ---
    # 1. Forward their message (text, photos, docs, etc.) to your admin chat
    forwarded_msg = await context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=user.id,
        message_id=message.message_id
    )

    # 2. Send an administrative context bubble right below it
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 **New message from:** {user.full_name} (@{user.username or 'No username'}, ID: `{user.id}`)\n*Hit 'Reply' on the forwarded message above to answer them.*",
        reply_to_message_id=forwarded_msg.message_id
    )

    # 3. Map this forwarded message's ID to the sender's user ID
    active_conversations[forwarded_msg.message_id] = user.id

    # 4. Acknowledge receipt to the user quietly
    await message.reply_text("Your message has been forwarded to the admin. You will receive a reply here if they choose to respond.")

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Handle text, photos, documents, and videos from users (ignoring commands)
    application.add_handler(MessageHandler(~filters.COMMAND, handle_message))

    print("WhisperInbox bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()