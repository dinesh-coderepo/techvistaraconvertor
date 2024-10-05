from app import app, scheduler

if __name__ == "__main__":
    try:
        scheduler.start()
        app.run(host="0.0.0.0", port=5000)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
