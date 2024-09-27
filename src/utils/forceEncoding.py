import sys
import codecs


# Force UTF-8 encoding for stdout and stderr (to allow printing emojis)
def forceEncoding():
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
