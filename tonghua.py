import vlc
import time

class VLCAudioPlayer:
    def __init__(self, rtmp_url):
        """Initialize the VLC audio player with the given RTMP URL."""
        self.rtmp_url = rtmp_url
        self.instance = vlc.Instance("--no-video")  # Disable video output
        self.media = self.instance.media_new(rtmp_url)
        self.player = self.instance.media_player_new()
        self.player.set_media(self.media)
        self.is_playing_audio = False

    def start(self):
        """Start playing the audio stream."""
        if not self.is_playing_audio:
            self.player.play()
            self.is_playing_audio = True
            print("Audio playback started.")

    def stop(self):
        """Stop playing the audio stream."""
        if self.is_playing_audio:
            self.player.stop()
            self.is_playing_audio = False
            print("Audio playback stopped.")

    def toggle_playback(self):
        """Toggle between play and stop states."""
        if self.is_playing_audio:
            self.stop()
        else:
            self.start()

    def set_volume(self, volume):
        """Set the audio volume (0-100)."""
        self.player.audio_set_volume(volume)
        print(f"Volume set to {volume}%.")

    def is_playing(self):
        """Check if the audio is currently playing."""
        return self.player.is_playing()
if __name__ == "__main__":
    # Initialize the audio player with an RTMP stream URL
    audio_player = VLCAudioPlayer("rtmp://0.0.0.0:8889/live2/stream")

    # Start the audio stream
    audio_player.start()

    try:
        while True:
            print("\nCommands: [start, stop, toggle, volume <value>, exit]")
            command = input("Enter command: ").strip().lower()

            if command == "start":
                audio_player.start()
            elif command == "stop":
                audio_player.stop()
            elif command == "toggle":
                audio_player.toggle_playback()
            elif command.startswith("volume"):
                try:
                    # Extract volume value
                    volume = int(command.split()[1])
                    if 0 <= volume <= 100:
                        audio_player.set_volume(volume)
                    else:
                        print("Volume must be between 0 and 100.")
                except (IndexError, ValueError):
                    print("Usage: volume <value> (value must be 0-100)")
            elif command == "exit":
                print("Exiting...")
                audio_player.stop()
                break
            else:
                print("Invalid command.")
    except KeyboardInterrupt:
        print("\nExiting...")
        audio_player.stop()
