# encoding: utf-8


try:
    import pygame
    from pygame import mixer
except ImportError:
    raise ImportError("\n<pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")


from time import time


class SoundObject:

    def __init__(self, sound_, priority_, name_, channel_, obj_id_):
        """
        CREATE A SOUND OBJECT CONTAINING CERTAIN ATTRIBUTES (SEE THE
        COMPLETE LIST BELOW)

        :param sound_   : Sound object; Sound object to play
        :param priority_: integer; Sound width in seconds
        :param name_    : string; Sound given name
        :param channel_ : integer; Channel to use
        :param obj_id_  : python int (C long long int); Sound unique ID
        """

        # SOUND OBJECT TO PLAY
        self.sound = sound_
        # RETURN THE LENGTH OF THIS SOUND IN SECONDS
        self.length = sound_.get_length()
        # SOUND PRIORITY - LOWEST TO HIGHEST (0 - 2)
        self.priority = priority_ if 0 < priority_ < 2 else 0
        # TIMESTAMP
        self.time = time()
        # SOUND NAME FOR IDENTIFICATION
        self.name = name_
        # CHANNEL USED
        self.active_channel = channel_
        # UNIQUE SOUND ID NUMBER
        self.obj_id = obj_id_
        # CLASS ID
        self.id = id(self)


class SoundControl(object):

    def __init__(self, screen_size_, channel_num_=8):

        # CHANNEL TO INIT
        self.channel_num = channel_num_
        # GET THE TOTAL NUMBER OF PLAYBACK CHANNELS
        # FIRST CHANNEL
        self.start = mixer.get_num_channels()
        # LAST CHANNEL
        self.end = self.channel_num + self.start
        # SETS THE NUMBER OF AVAILABLE CHANNELS FOR THE MIXER.
        mixer.set_num_channels(self.end)

        # RESERVE CHANNELS FROM BEING AUTOMATICALLY USED
        mixer.set_reserved(self.end)

        # CREATE A CHANNEL OBJECT FOR CONTROLLING PLAYBACK
        self.channels = [mixer.Channel(j + self.start) for j in range(self.channel_num)]

        # LIST OF UN-INITIALISED OBJECTS
        self.snd_obj = [None] * self.channel_num

        # POINTER TO THE BOTTOM OF THE STACK
        self.channel = self.start

        # CREATE A LIST WITH ALL CHANNEL NUMBER
        self.all = list(range(self.start, self.end))

        self.screen_size = screen_size_

    def update(self):
        """
        CLEAR THE LIST SND_OBJ WHEN THE
        CHANNEL IS NOT BUSY (SOUND PLAYED)
        """

        i = 0
        snd_obj = self.snd_obj

        for c in self.channels:
            if c:
                if not c.get_busy():
                    snd_obj[i] = None
            i += 1

    def update_volume(self, volume_=1.0):
        """
        UPDATE ALL SOUND OBJECT TO A SPECIFIC VOLUME.
        THIS HAS IMMEDIATE EFFECT AND DO NOT FADE THE SOUND

        :param volume_: float; volume value, default is 1.0
        :return: None
        """
        # SET THE VOLUME IN CASE OF AN INPUT ERROR
        if 0.0 >= volume_ >= 1.0:
            volume_ = 1.0
        # SET THE VOLUME FOR ALL SOUNDS
        for c in self.channels:
            c.set_volume(volume_)

    def show_free_channels(self):
        """
        RETURN A LIST OF FREE CHANNELS (NUMERICAL VALUES).
        :return: list; RETURN A LIST
        """

        free_channels = []
        i = 0
        free_channels_append = free_channels.append
        start = self.start

        for c in self.channels:
            if not c.get_busy():
                free_channels_append(i + start)
            i += 1

        return free_channels

    def show_sounds_playing(self):
        """
        DISPLAY ALL SOUNDS OBJECTS
        """
        i = 0
        snd_obj = self.snd_obj

        j = 0
        for object_ in self.snd_obj:
            if object_:
                print('\nName %s  id %s priority %s  channel %s width %s time left %s ' %
                      (object_.name, object_.priority, object_.active_channel, round(object_.length),
                 round(snd_obj.length - (time() - snd_obj.time))))
            j += 1

    def get_identical_sounds(self, sound):
        """
        RETURN A LIST OF CHANNEL(S) PLAYING IDENTICAL SOUND OBJECT(s)

        :param sound: Mixer object; Object to compare to
        :return: python list; List containing channels number
        playing similar sound object
        """

        duplicate = []
        duplicate_append = duplicate.append

        for obj in self.snd_obj:
            if obj:
                if obj.sound == sound:
                    duplicate_append(obj.active_channel)
        return duplicate

    def get_identical_id(self, id_):
        """
        RETURN A LIST CONTAINING ANY IDENTICAL SOUND BEING MIXED.
        USE THE UNIQUE ID FOR REFERENCING OBJECTS

        :param id_: python integer; unique id number that reference a sound object
        :return: list; Return a list of channels containing identical sound object
        """

        duplicate = []
        duplicate_append = duplicate.append

        for obj in self.snd_obj:
            if obj:
                if obj.obj_id == id_:
                    duplicate_append(obj)
        return duplicate

    def stop(self, stop_list):
        """
        STOP ALL SOUND BEING PLAYED ON THE GIVEN LIST OF CHANNELS.
        ONLY SOUND WITH PRIORITY LEVEL 0 CAN BE STOPPED.

        :param stop_list: python list; list of channels
        :return: None
        """

        start = self.start
        snd_obj = self.snd_obj
        channels = self.channels

        for c in stop_list:
                l = c - start
                if snd_obj[l]:
                    if snd_obj[l].priority == 0:
                        channels[l].set_volume(0.0, 0.0)
                        channels[l].stop()
        self.update()

    def stop_all_except(self, exception=None):
        """
        STOP ALL SOUND OBJECT EXCEPT SOUNDS FROM A GIVEN LIST OF ID(SOUND)
        IT WILL STOP SOUND PLAYING ON ALL CHANNELS REGARDLESS
        OF THEIR PRIORITY.

        :exception: Can be a single pygame.Sound id value or a list containing
        all pygame.Sound object id numbers.
        """
        # EXCEPTION MUST BE DEFINED
        assert exception is None, "\nArgument exception is not defined."

        if not isinstance(exception, list):
            exception = [exception]


        start = self.start
        snd_obj = self.snd_obj
        channels = self.channels

        for c in self.all:
            l = c - start
            snd_object = snd_obj[l]
            if snd_object:
                if snd_object.obj_id not in exception:
                    channels[l].set_volume(0.0)
                    channels[l].stop()
        self.update()

    def stop_all(self):
        """ STOP ALL SOUNDS NO EXCEPTIONS."""

        start = self.start
        snd_obj = self.snd_obj
        channels = self.channels

        for c in self.all:
            l = c - start
            snd_object = snd_obj[l]
            if snd_object:
                channels[l].set_volume(0.0)
                channels[l].stop()
        self.update()

    def stop_name(self, name_):
        """
        STOP A PYGAME.SOUND OBJECT IF PLAYING ON ANY OF THE CHANNELS.
        NAME_ REFER TO THE NAME GIVEN TO THE SOUND WHEN INSTANTIATED (E.G 'WHOOSH' NAME BELOW)
        GL.MIXER_PLAYER.PLAY(SOUND_=WHOOSH, LOOP_=FALSE, PRIORITY_=0, VOLUME_=GL.SOUND_LEVEL,
                FADE_OUT_MS=0, PANNING_=FALSE, NAME_='WHOOSH', X_=0)
        """
        channels = self.channels
        start = self.start

        for sound in self.snd_obj:
            if sound and sound.name == name_:
                try:
                    channels[sound.active_channel - start].set_volume(0.0)
                    channels[sound.active_channel - start].stop()
                except IndexError:
                    # IGNORE ERROR
                    ...
        self.update()

    def stop_object(self, object_id):
        """ STOP A GIVEN SOUND USING THE PYGAME.SOUND OBJECT ID NUMBER. """

        channels = self.channels
        start = self.start

        for sound in self.snd_obj:
            if sound and sound.obj_id == object_id:
                try:
                    channels[sound.active_channel - start].set_volume(0.0)
                    channels[sound.active_channel - start].stop()
                except IndexError:
                    # IGNORE ERROR
                    ...

        self.update()

    def show_time_left(self, object_id):
        """
        RETURN THE TIME LEFT
        :param object_id: python integer; unique object id
        :return: a float representing the time left in seconds.
        """
        j = 0
        snd_obj = self.snd_obj
        for obj in snd_obj:
            if obj:
                if obj.obj_id == object_id:
                    return round(snd_obj[j].length - (time() - snd_obj[j].time))
            j += 1
        return 0.0

    def get_reserved_channels(self):
        """ RETURN THE NUMBER OF RESERVED CHANNELS """
        return self.channel_num

    def get_reserved_start(self):
        """ RETURN THE FIRST RESERVED CHANNEL NUMBER """
        return self.start

    def get_reserved_end(self):
        """ RETURN THE LAST RESERVED CHANNEL NUMBER """
        return self.end

    def get_channels(self):
        """
        RETURN A LIST OF ALL RESERVED PYGAME MIXER CHANNELS.
        """
        return self.channels

    def get_sound(self, channel_):
        """
        RETURN THE SOUND BEING PLAYED ON A SPECIFIC CHANNEL (PYGAME.MIXER.CHANNEL)

        :param channel_: integer;  channel_ is an integer representing the channel number.
        """
        try:
            sound = self.channels[channel_]
        except IndexError:
            raise Exception('\nIndexError: Channel number out of range ')
        else:
            return sound

    def get_sound_object(self, channel_):
        """
        RETURN A SPECIFIC SOUND OBJECT
        RETURN NONE IN CASE OF AN INDEX ERROR
        """
        try:
            s = self.snd_obj[channel_]
        except IndexError:
            return None
        else:
            return s

    def get_all_sound_object(self):
        """ RETURN ALL SOUND OBJECTS """
        return self.snd_obj

    def play(self, sound_, loop_, priority_=0, volume_=1.0,
             fade_in_ms=100.0, fade_out_ms=100.0, panning_=False, name_=None,
             x_=None, object_id_=None):

        """
        PLAY A SOUND OBJECT ON THE GIVEN CHANNEL
        RETURN NONE IF ALL CHANNELS ARE BUSY OR IF AN EXCEPTION IS RAISED


        :param sound_       : pygame mixer sound
        :param loop_        : loop the sound indefinitely -1
        :param priority_    : Set the sound priority (low : 0, med : 1, high : 2)
        :param volume_      : Set the sound volume 0.0 to 1.0 (100% full volume)
        :param fade_in_ms   : Fade in sound effect in ms
        :param fade_out_ms  : float; Fade out sound effect in ms
        :param panning_     : boolean for using panning method (stereo mode)
        :param name_        : String representing the sound name
        :param x_           : Sound position for stereo mode,
        :param object_id_   : unique sound id
        """

        l            = 0
        channels     = self.channels
        channel      = self.channel
        start        = self.start
        end          = self.end
        screen_width = self.screen_size.w

        left  = 0
        right = 0

        try:
            if not sound_:
                raise AttributeError('\nArgument sound_ cannot be None')

            if x_ is None or (0 > x_ > screen_width):
                x_ = screen_width >> 1

            if name_ is None:
                name_ = str(id(sound_))

            if object_id_ is None:
                object_id_ = id(sound_)

            l = channel - start
            # TODO OVERFLOW CHANNELS[l]
            # CHECK IF CURRENT CHANNEL IS BUSY
            if channels[l].get_busy() == 0:

                # PLAY A SOUND IN STEREO MODE
                if panning_:
                    left, right = self.stereo_panning(x_, self.screen_size.w)
                    channels[l].set_volume(left * volume_, right * volume_)

                else:
                    channels[l].set_volume(volume_)

                channels[l].fadeout(fade_out_ms)
                channels[l].play(sound_, loops=loop_, maxtime=0, fade_ms=fade_out_ms)

                self.snd_obj[l] = SoundObject(sound_, priority_, name_, channel, object_id_)

                # PREPARE THE MIXER FOR THE NEXT CHANNEL
                self.channel += 1

                if self.channel > end - 1:
                    self.channel = start

                # RETURN THE CHANNEL NUMBER PLAYING THE SOUND OBJECT
                return channel - 1

            # ALL CHANNELS ARE BUSY
            else:
                self.stop(self.get_identical_sounds(sound_))
                # VERY IMPORTANT, GO TO NEXT CHANNEL.
                self.channel += 1
                if self.channel > end - 1:
                    self.channel = start
                return None

        except IndexError as e:
            print('\n[-] SoundControl error : %s ' % e)
            print(self.channel, l)
            return None

    def display_size_update(self, rect_):
        """
        UPDATE THE SCREEN SIZE AFTER CHANGING MODE
        THIS FUNCTION IS MAINLY USED FOR THE PANNING MODE (STEREO)
        :param rect_: pygame.Rect; display dimension
        :return: None
        """
        self.screen_size = rect_

    def stereo_panning(self, x_, screen_width):
        """
        STEREO MODE

        :param screen_width: display width
        :param x_          : integer; x value of sprite position on screen
        :return: tuple of float;
        """
        right_volume = 0.0
        left_volume  = 0.0

        # MUTE THE SOUND IF OUTSIDE THE BOUNDARIES
        if 0 > x_ > screen_width:
            return right_volume, left_volume

        right_volume = float(x_) / screen_width
        left_volume  = 1.0 - right_volume

        return left_volume, right_volume
