import xmltodict
import isodate
import requests

# Assuming mainLogic.error.debugger and mainLogic.error.AdaptationSetIsNotVideo are defined elsewhere
# For example:
class Debugger:
    def info(self, msg): print(f"INFO: {msg}")
    def debug(self, msg): print(f"DEBUG: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")

debugger = Debugger() # Placeholder

class AdaptationSetIsNotVideo(Exception):
    """Custom exception for when an adaptation set is not video."""
    pass


class MPDParser:
    def __init__(self, url, extractSignature=True, signature=None, verbose=True):
        self.url = url
        self.base_url = ""
        self.extractSignature = extractSignature
        self.verbose = verbose
        self.signature = signature
        self.mpd_dict = None
        self.audio_set = None
        self.video_set = None
        self.audio_segment_template = None
        self.video_segment_template = None

    def pre_process(self):
        if self.extractSignature:
            if "?" in self.url:
                self.base_url, self.signature = self.url.split("?", 1) # Split only on the first ?
                if self.base_url.endswith("/master.mpd"):
                    self.base_url = self.base_url.split("master.mpd")[0]
                if self.verbose:
                    debugger.info(f"Base-Url {self.base_url}")
                    debugger.info(f"Signature {self.signature}")
        elif not self.base_url and "/" in self.url: # Basic Base URL extraction if no signature
             self.base_url = self.url.rsplit('/', 1)[0] + "/"
             if self.base_url.endswith("master.mpd/"): # if master.mpd was part of path
                 self.base_url = self.base_url.split("master.mpd/")[0]


        return self

    def build_url(self, media, segment=None):
        if self.base_url:
            if media.startswith("http"):
                return media
            else:
                # Ensure base_url ends with / and media doesn't start with /
                processed_base_url = self.base_url
                if not processed_base_url.endswith('/'):
                    processed_base_url += '/'
                
                processed_media = media
                if processed_media.startswith('/'):
                    processed_media = processed_media[1:]

                url = f"{processed_base_url}{processed_media}"
                if segment is not None:
                    url = url.replace("$Number$", str(segment))
                return f"{url}?{self.signature}" if self.signature else url
        else:
            # If no base_url, assume media is a full URL or relative to current path
            # This part might need adjustment depending on how relative URLs without base_url are handled
            url = media
            if segment is not None:
                url = url.replace("$Number$", str(segment))
            return f"{url}?{self.signature}" if self.signature else url


    def load_manifest(self):
        # if self.base_url: # Original check was if base_url is present, but manifest URL is self.url
        response = requests.get(self.url)
        if response.status_code == 200:
            if self.verbose: # Moved verbose logging here
                debugger.debug(f"Response from {self.url}")
                debugger.debug(f"Status code {response.status_code}")
            return response.text
        else:
            debugger.error(f"Failed to load manifest from {self.url}. Status: {response.status_code}")
        return None

    def to_dict(self, xml_string):
        """Convert XML string to dictionary."""
        if not xml_string:
            raise ValueError("Cannot parse None or empty XML string.")
        return xmltodict.parse(xml_string, process_namespaces=False)

    def parse(self):
        manifest_xml = self.load_manifest()
        if manifest_xml:
            self.mpd_dict = self.to_dict(manifest_xml)
        else:
            # Ensure mpd_dict is not None if parsing fails, to prevent subsequent errors
            self.mpd_dict = {} # Or raise an error
            raise ValueError("Failed to load or parse MPD manifest.")
        return self

    def get_duration(self):
        """Get the duration of the media from the MPD dictionary."""
        if "MPD" in self.mpd_dict and "@mediaPresentationDuration" in self.mpd_dict["MPD"]:
            duration_str = self.mpd_dict["MPD"]["@mediaPresentationDuration"]
            return isodate.parse_duration(duration_str)
        raise ValueError("Duration not found in MPD dictionary.")

    def get_adaptation_sets(self):
        """Get the adaptation sets from the MPD dictionary."""
        try:
            period = self.mpd_dict["MPD"]["Period"]
            # Period can be a list or a dict. Handle both.
            if isinstance(period, list):
                # Assuming we are interested in the first period if multiple exist
                # Or you might need a way to select a specific period
                return period[0]["AdaptationSet"]
            return period["AdaptationSet"]
        except KeyError:
            raise ValueError("Adaptation sets not found in MPD dictionary (MPD/Period/AdaptationSet path invalid).")
        except TypeError: # handles case where self.mpd_dict might be None or not a dict
             raise ValueError("MPD dictionary is not properly initialized or structured.")


    def get_audio_set(self):
        """Get the audio adaptation set from the MPD dictionary."""
        if not self.audio_set:
            adaptation_sets = self.get_adaptation_sets()
            # AdaptationSet can be a list or a single dict
            if not isinstance(adaptation_sets, list):
                adaptation_sets = [adaptation_sets]
            for adaptation_set in adaptation_sets:
                if "@contentType" in adaptation_set and adaptation_set["@contentType"] == "audio":
                    self.audio_set = adaptation_set
                    return self.audio_set
            raise ValueError("Audio adaptation set not found in MPD dictionary.")
        return self.audio_set

    def get_video_set(self):
        """Get the video adaptation set from the MPD dictionary."""
        if not self.video_set:
            adaptation_sets = self.get_adaptation_sets()
            # AdaptationSet can be a list or a single dict
            if not isinstance(adaptation_sets, list):
                adaptation_sets = [adaptation_sets]
            for adaptation_set in adaptation_sets:
                if "@contentType" in adaptation_set and adaptation_set["@contentType"] == "video":
                    self.video_set = adaptation_set
                    return self.video_set
            raise ValueError("Video adaptation set not found in MPD dictionary.")
        return self.video_set

    def get_resolutions_in_adaptation_set(self, adaptation_set):
        """Get the resolutions available in the adaptation set."""
        resolutions = []
        if "Representation" not in adaptation_set:
            raise AdaptationSetIsNotVideo("No Representation found in AdaptationSet")

        representations = adaptation_set["Representation"]
        if not isinstance(representations, list):
            representations = [representations] # Handle single Representation case

        for representation in representations:
            if "@height" in representation:
                resolutions.append(int(representation["@height"]))
            else:
                # If one representation doesn't have height, it might not be purely video representations
                debugger.warning("Representation found without @height attribute in video AdaptationSet.")


        if not resolutions: # If no heights were found at all
             raise AdaptationSetIsNotVideo("No heights found in any Representation; AdaptationSet may not be video or is malformed.")
        return resolutions


    @staticmethod
    def get_timeline_info(segment_template):
        """Get the timescale from the adaptation set."""
        if "SegmentTimeline" in segment_template and "S" in segment_template["SegmentTimeline"]:
            s_elements = segment_template["SegmentTimeline"]["S"]
            # If there's only one S element, it might not be a list
            if not isinstance(s_elements, list):
                return [s_elements]
            return s_elements
        return None

    @staticmethod
    def process_timeline(timeline):
        """Process timeline to extract first and last elements."""
        if not timeline: # Handles None or empty list
            return None, None
        return timeline[0], timeline[-1]

    def get_segment_template(self, adaptation_set, representation_index=0, video_type="720"):
        """Get the segment template from the adaptation set."""
        
        selected_representation = None
        representations = adaptation_set.get("Representation")

        if not representations:
            raise ValueError("No Representation found in AdaptationSet.")
        
        # Ensure representations is a list
        if not isinstance(representations, list):
            representations = [representations]

        if "video" in adaptation_set.get("@contentType", ""):
            found_representation = False
            for i, representation in enumerate(representations):
                if representation.get("@height") == video_type:
                    selected_representation = representation
                    representation_index = i # Update index if we find the specific type
                    found_representation = True
                    break
            if not found_representation and representations: # Default to first representation if specific video_type not found
                selected_representation = representations[representation_index if representation_index < len(representations) else 0]
            
            if selected_representation:
                 self.video_segment_template = selected_representation.get("SegmentTemplate")
            else: # Should not happen if representations is not empty
                 raise ValueError("Video representation not found.")

        elif "audio" in adaptation_set.get("@contentType", ""):
            # For audio, typically use the first representation or one specified by index
            if representations:
                 selected_representation = representations[representation_index if representation_index < len(representations) else 0]
                 self.audio_segment_template = selected_representation.get("SegmentTemplate")
            else:
                 raise ValueError("Audio representation not found.")
        else:
            raise ValueError("Adaptation set is not video or audio")

        segment_template_dict = selected_representation.get("SegmentTemplate")
        if not segment_template_dict:
            raise ValueError("SegmentTemplate not found in the selected Representation.")

        return (
            segment_template_dict,
            segment_template_dict["@startNumber"],
            segment_template_dict["@initialization"],
            segment_template_dict["@media"],
            segment_template_dict["@timescale"]
        )

    def get_segment_urls(self):
        """Get all segment URLs for both video and audio."""
        result = {
            'video': {'init': None, 'segments': {}},
            'audio': {'init': None, 'segments': {}}
        }

        # Process video segments
        video_set = self.get_video_set()
        video_template, vid_start_number_str, vid_init, vid_media, vid_timescale = self.get_segment_template(video_set, video_type="720")
        vid_timeline = self.get_timeline_info(video_template)
        vid_first_elem, _ = self.process_timeline(vid_timeline) # This line was in original, kept for consistency

        result['video']['init'] = self.build_url(vid_init)

        # This 'end' variable will hold the total count of video segments,
        # which is also the last segment number if startNumber is "1".
        end = 0 # Renaming to 'video_total_segments_count' for clarity internally, but original used 'end'
        if vid_timeline:
            for _, S_element in enumerate(vid_timeline): # _ is index, S_element is the S dict
                if "@r" in S_element:
                    end += int(S_element["@r"])
                end += 1 # Increment for the S_element itself

        if self.verbose:
             debugger.debug(f"Total video segments (from original 'end' logic): {end}")


        if vid_timeline:
            # Loop from int(vid_start_number_str) up to 'end' (inclusive, as 'end' is last segment number when startNumber=1)
            for i in range(int(vid_start_number_str), end + 1):
                result['video']['segments'][i] = self.build_url(vid_media, i)

        # Process audio segments
        audio_set = self.get_audio_set()
        audio_template, aud_start_number_str, aud_init, aud_media, aud_timescale = self.get_segment_template(audio_set)
        aud_timeline = self.get_timeline_info(audio_template)

        result['audio']['init'] = self.build_url(aud_init)

        if aud_timeline:
            audio_total_segments = 0
            # Correctly calculate total number of audio segments, including repeats
            for S_element in aud_timeline:
                audio_total_segments += 1  # For the S_element itself
                if "@r" in S_element:
                    audio_total_segments += int(S_element["@r"]) # Add the repeat count
            
            if self.verbose:
                debugger.debug(f"Calculated total audio segments: {audio_total_segments}")

            # Generate audio segment URLs
            # If aud_start_number_str is "1", segments are 1, 2, ..., audio_total_segments.
            # The loop should go from int(aud_start_number_str) up to audio_total_segments (inclusive).
            for i in range(int(aud_start_number_str), audio_total_segments + 1):
                result['audio']['segments'][i] = self.build_url(aud_media, i)
        
        return result
