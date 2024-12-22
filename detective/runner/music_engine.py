import pygame
import os
import time
import random


""" 
This module plays music from a directory with different modes and volume control
using Pygame. It also decodes gestures to control the music playback.

gesture_decode(gesture):
    
    returns:
    ch_mode, volume_up, volume_down, pause, resume, play_next


    if gesture == "OK":
        ch_mode = True
    elif gesture == "Like":
        play_next = True
    elif gesture == "Return":
        resume = True
    elif gesture == "Pause":
        pause = True
    elif gesture == "Right":
        volume_down = True
    elif gesture == "Left":
        volume_up = True
    else:
        ch_mode = False
        volume_up = False
        volume_down = False
"""


class MusicPlayer:
    def __init__(
        self, music_dir, volume_step=5, volume_update_interval=0.5
    ):
        pygame.init()
        pygame.mixer.init()

        self.music_dir = music_dir
        self.playlist = self.load_playlist()
        self.current_track_index = 0
        self.ch_mode = "sequence"  # "sequence", "shuffle", "single"
        self.volume = 50  # Initial volume
        pygame.mixer.music.set_volume(self.volume / 100.0)
        self.is_playing = False
        self.last_gesture = None
        self.volume_timer = 0
        self.volume_step = volume_step
        self.volume_update_interval = volume_update_interval
        self.load_current_track()

    def load_playlist(self):
        """Loads all .mp3 and .wav files from the music directory into a playlist."""
        playlist = []
        for filename in os.listdir(self.music_dir):
            if filename.endswith((".mp3", ".wav")):  # Add other audio formats if needed
                playlist.append(os.path.join(self.music_dir, filename))
        if not playlist:
            print(
                "Warning: no music file detected, please check ./assets/music directory"
            )
        return playlist

    def load_current_track(self):
        """Loads the current track from the playlist."""
        if 0 <= self.current_track_index < len(self.playlist):
            try:
                pygame.mixer.music.load(self.playlist[self.current_track_index])
                print(f"Loaded track: {self.playlist[self.current_track_index]}")
            except pygame.error as e:
                print(f"Error loading track: {self.playlist[self.current_track_index]}")
                print(e)
                # Handle the error (e.g., remove the track from the playlist, skip to the next)
                self.playlist.pop(self.current_track_index)
                self.current_track_index = max(
                    0, self.current_track_index - 1
                )  # prevent index out of range
                self.load_current_track()  # recursively load next track

    def play_music(self):
        """Plays the current track."""
        if self.playlist:
            pygame.mixer.music.play()
            self.is_playing = True

    def gesture_decode(self, gesture):
        current_time = time.time()

        # Edge detection for ch_mode, play_next, pause, resume
        if gesture != self.last_gesture:
            if gesture == "OK":
                self.toggle_ch_mode()
                print(f"Change mode toggled to: {self.ch_mode}")
            elif gesture == "Like":
                self.play_next()
                print("Play next")
            elif gesture == "Return":
                if not self.is_playing:
                    self.resume()
                    print("Resume")
            elif gesture == "Pause":
                if self.is_playing:
                    self.pause()
                    print("Pause")

        # Volume control with timer
        if gesture == "Right":
            if current_time - self.volume_timer > self.volume_update_interval:
                self.volume_down()
                self.volume_timer = current_time
        elif gesture == "Left":
            if current_time - self.volume_timer > self.volume_update_interval:
                self.volume_up()
                self.volume_timer = current_time

        self.last_gesture = gesture

        # Check if the current song has ended
        if self.is_playing and not pygame.mixer.music.get_busy():
            self.handle_song_end()

    def toggle_ch_mode(self):
        if self.ch_mode == "sequence":
            self.ch_mode = "shuffle"
        elif self.ch_mode == "shuffle":
            self.ch_mode = "single"
        else:
            self.ch_mode = "sequence"

    def volume_up(self):
        self.volume = min(100, self.volume + self.volume_step)
        pygame.mixer.music.set_volume(self.volume / 100.0)
        print(f"Volume up: {self.volume}")

    def volume_down(self):
        self.volume = max(0, self.volume - self.volume_step)
        pygame.mixer.music.set_volume(self.volume / 100.0)
        print(f"Volume down: {self.volume}")

    def pause(self):
        pygame.mixer.music.pause()
        self.is_playing = False

    def resume(self):
        pygame.mixer.music.unpause()
        self.is_playing = True

    def play_next(self):
        if self.ch_mode == "sequence":
            self.current_track_index = (self.current_track_index + 1) % len(
                self.playlist
            )
        elif self.ch_mode == "shuffle":
            self.current_track_index = random.randint(0, len(self.playlist) - 1)
        # "single" mode doesn't change the track
        self.load_current_track()
        self.play_music()

    def handle_song_end(self):
        if self.ch_mode == "sequence":
            self.current_track_index = (self.current_track_index + 1) % len(
                self.playlist
            )
        elif self.ch_mode == "shuffle":
            self.current_track_index = random.randint(0, len(self.playlist) - 1)
        # In "single" mode, we just stop
        if self.ch_mode != "single":
            self.load_current_track()
            self.play_music()

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False


if __name__ == "__main__":
    # Simulate receiving gestures from a camera
    from queue import Queue

    gestures = [
        "None",
        "None",
        "OK",
        "OK",
        "OK",
        "Right",
        "Right",
        "Right",
        "Pause",
        "Pause",
        "Left",
        "Left",
        "Left",
        "Left",
        "Return",
        "Return",
        "Like",
        "Like",
    ]
    gesture_queue = Queue()
    for gesture in gestures:
        gesture_queue.put(gesture)

    def music_play(music_dir, resent_gesture_queue, initial_volume=50):
        try:
            music_player = MusicPlayer(music_dir=music_dir)
            music_player.volume = initial_volume
            pygame.mixer.music.set_volume(music_player.volume / 100.0)
            music_player.play_music()

            while True:
                if not resent_gesture_queue.empty():
                    gesture = resent_gesture_queue.get()
                    music_player.gesture_decode(gesture)
                time.sleep(0.1)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            pygame.quit()

    music_play("assets/music", gesture_queue)
