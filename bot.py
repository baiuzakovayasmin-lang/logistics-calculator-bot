
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

import os
TOKEN = os.getenv("TOKEN")

TRANSPORT, WEIGHT, DISTANCE, VALUE = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "? Logistics Cost Calculator\n\n"
        "Send /calculate to start."
    )


async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "? Choose transport:\n\n"
        "Type: Road or Rail"
    )
    return TRANSPORT


async def transport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.message.text.strip().lower()

    if answer not in ["road", "rail"]:
        await update.message.reply_text(
            "? Please type exactly: Road or Rail"
        )
        return TRANSPORT

    context.user_data["transport"] = answer

    await update.message.reply_text(
        "? Enter cargo weight in tons:"
    )

    return WEIGHT


async def weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        weight_value = float(update.message.text.replace(",", "."))
    except ValueError:
        await update.message.reply_text(
            "? Please enter a number, for example: 12"
        )
        return WEIGHT

    context.user_data["weight"] = weight_value

    await update.message.reply_text(
        "? Enter distance in km:"
    )

    return DISTANCE


async def distance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        distance_value = float(update.message.text.replace(",", "."))
    except ValueError:
        await update.message.reply_text(
            "? Please enter a number, for example: 500"
        )
        return DISTANCE

    context.user_data["distance"] = distance_value

    await update.message.reply_text(
        "? Enter cargo value in KZT:"
    )

    return VALUE


async def value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        cargo_value = float(
            update.message.text.replace(" ", "").replace(",", ".")
        )
    except ValueError:
        await update.message.reply_text(
            "? Please enter a number, for example: 9000000"
        )
        return VALUE

    transport = context.user_data["transport"]
    distance = context.user_data["distance"]
    weight = context.user_data["weight"]

    # Transport costs
    if transport == "road":
        transport_cost = distance * 46 + 1050
        loading = 35000
        terminal = 0
        storage = 12000 * 1

    else:
        transport_cost = 18500
        loading = 0
        terminal = 80000
        storage = 9000 * 2

    # Insurance
    insurance = cargo_value * 0.0035

    # Total
    total = (
        transport_cost
        + loading
        + terminal
        + storage
        + insurance
    )

    await update.message.reply_text(
        f"? CALCULATION RESULT\n\n"
        f"? Transport: {transport.title()}\n"
        f"? Cargo weight: {weight:g} tons\n"
        f"? Distance: {distance:g} km\n"
        f"? Cargo value: {cargo_value:,.0f} KZT\n\n"
        f"? Transport cost: {transport_cost:,.0f} KZT\n"
        f"? Loading: {loading:,.0f} KZT\n"
        f"? Terminal: {terminal:,.0f} KZT\n"
        f"? Storage: {storage:,.0f} KZT\n"
        f"? Insurance: {insurance:,.0f} KZT\n\n"
        f"? TOTAL: {total:,.0f} KZT"
    )

    return ConversationHandler.END


def main():

    app = Application.builder().token(TOKEN).build()

    conversation = ConversationHandler(
        entry_points=[
            CommandHandler("calculate", calculate)
        ],

        states={
            TRANSPORT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    transport
                )
            ],

            WEIGHT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    weight
                )
            ],

            DISTANCE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    distance
                )
            ],

            VALUE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    value
                )
            ],
        },

        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conversation)

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
