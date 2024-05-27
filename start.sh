# ==============================================================================
# = Lucci Auto-start Script                                                    =
# = -------------------------------------------------------------------------- =
# = This is a small script which is meant to manage the bot in a Linux         =
# = environment. This requires screen to be installed to work and it is        =
# = recommended to either create a service with this code or just hook the     =
# = code up to a crontab file                                                  =
# ==============================================================================
if ! screen -list | grep "Lucci"; then
    screen -dmS Lucci bash -c 'python3 main.py'
fi
