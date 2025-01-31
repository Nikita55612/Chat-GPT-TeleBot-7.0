import bot
import time


def main():
    try:
        print("bot start polling...")
        bot.bot.infinity_polling()
    except Exception as ex:
        time.sleep(20)
        main()


if __name__ == "__main__":
    main()