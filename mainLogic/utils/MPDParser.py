import xmltodict
import isodate
import requests

from mainLogic.error import debugger, AdaptationSetIsNotVideo


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
                self.base_url, self.signature = self.url.split("?")
                if self.base_url.endswith("/master.mpd"):
                    self.base_url = self.base_url.split("master.mpd")[0]
                if self.verbose:
                    debugger.info(f"Base-Url {self.base_url}")
                    debugger.info(f"Signature {self.signature}")
        return self

    def build_url(self, media, segment=None):
        if self.base_url:
            if media.startswith("http"):
                return media
            else:
                url = f"{self.base_url}{media}"
                if segment is not None:
                    url = url.replace("$Number$", str(segment))
                return f"{url}?{self.signature}" if self.signature else url
        else:
            return media

    def load_manifest(self):
        if self.base_url:
            response = requests.get(self.url)
            if response.status_code == 200:
                debugger.debug(f"Response from {self.url}")
                debugger.debug(f"Status code {response.status_code}")
                return response.text
        return None

    def to_dict(self, xml_string):
        """Convert XML string to dictionary."""
        return xmltodict.parse(xml_string, process_namespaces=False)

    def parse(self):
        self.mpd_dict = self.to_dict(self.load_manifest())
        return self

    def get_duration(self):
        """Get the duration of the media from the MPD dictionary."""
        if "MPD" in self.mpd_dict and "@mediaPresentationDuration" in self.mpd_dict["MPD"]:
            duration = self.mpd_dict["MPD"]["@mediaPresentationDuration"]
            return isodate.parse_duration(duration)
        raise ValueError("Duration not found in MPD dictionary.")

    def get_adaptation_sets(self):
        """Get the adaptation sets from the MPD dictionary."""
        if "MPD" in self.mpd_dict and "Period" in self.mpd_dict["MPD"]:
            return self.mpd_dict["MPD"]["Period"]["AdaptationSet"]
        raise ValueError("Adaptation sets not found in MPD dictionary.")

    def get_audio_set(self):
        """Get the audio adaptation set from the MPD dictionary."""
        if not self.audio_set:
            adaptation_sets = self.get_adaptation_sets()
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
            for adaptation_set in adaptation_sets:
                if "@contentType" in adaptation_set and adaptation_set["@contentType"] == "video":
                    self.video_set = adaptation_set
                    return self.video_set
            raise ValueError("Video adaptation set not found in MPD dictionary.")
        return self.video_set

    def get_resolutions_in_adaptation_set(self, adaptation_set):
        """Get the resolutions available in the adaptation set."""
        if isinstance(adaptation_set["Representation"], list):
            return [int(representation["@height"]) for representation in adaptation_set["Representation"]]
        raise AdaptationSetIsNotVideo()

    @staticmethod
    def get_timeline_info(segment_template):
        """Get the timescale from the adaptation set."""
        if "SegmentTimeline" in segment_template and "S" in segment_template["SegmentTimeline"]:
            return segment_template["SegmentTimeline"]["S"]
        return None

    @staticmethod
    def process_timeline(timeline):
        """Process timeline to extract first and last elements."""
        if not timeline:
            return None, None
        return timeline[0], timeline[-1]

    def get_segment_template(self, adaptation_set, representation_index=0, video_type="720"):
        """Get the segment template from the adaptation set."""
        if isinstance(adaptation_set["Representation"], list) and "video" in adaptation_set["@contentType"]:
            for i, representation in enumerate(adaptation_set["Representation"]):
                if representation["@height"] == video_type:
                    representation_index = i
            segment_template = adaptation_set["Representation"][representation_index]["SegmentTemplate"]
            self.video_segment_template = segment_template
        elif "audio" in adaptation_set["@contentType"]:
            segment_template = adaptation_set["Representation"]["SegmentTemplate"]
            self.audio_segment_template = segment_template
        else:
            raise ValueError("Adaptation set is not video or audio")

        return (
            segment_template,
            segment_template["@startNumber"],
            segment_template["@initialization"],
            segment_template["@media"],
            segment_template["@timescale"]
        )

    def get_segment_urls(self):
        """Get all segment URLs for both video and audio."""
        result = {
            'video': {'init': None, 'segments': {}},
            'audio': {'init': None, 'segments': {}}
        }

        # Process video segments
        video_set = self.get_video_set()
        video_template, vid_start_number, vid_init, vid_media, vid_timescale = self.get_segment_template(video_set, video_type="720")
        vid_timeline = self.get_timeline_info(video_template)
        vid_first_elem, _ = self.process_timeline(vid_timeline)

        # Add video init URL
        result['video']['init'] = self.build_url(vid_init)

        end = 0

        for _, S in enumerate(vid_timeline):
            if "@r" in S:
                end += int(S["@r"])
            end+=1

        debugger.debug(f"Video start {end}")

        if vid_timeline:
            for i in range(int(vid_start_number), int(end) +1):
                result['video']['segments'][i] = self.build_url(vid_media, i)

        # Process audio segments
        audio_set = self.get_audio_set()
        audio_template, aud_start_number, aud_init, aud_media, aud_timescale = self.get_segment_template(audio_set)
        aud_timeline = self.get_timeline_info(audio_template)

        # Add audio init URL
        result['audio']['init'] = self.build_url(aud_init)

        if aud_timeline:
            # Generate audio segment URLs
            for i in range(int(aud_start_number), len(aud_timeline) + 1):
                result['audio']['segments'][i] = self.build_url(aud_media, i)

        return result

#
# url = "https://sec-prod-mediacdn.pw.live/df96bea5-a4cb-487a-8ed7-8087dffd92c8/master.mpd?URLPrefix=aHR0cHM6Ly9zZWMtcHJvZC1tZWRpYWNkbi5wdy5saXZlL2RmOTZiZWE1LWE0Y2ItNDg3YS04ZWQ3LTgwODdkZmZkOTJjOA&Expires=1746006867&KeyName=pw-prod-key&Signature=cXxu3O_EzH8HFqHU3KW3dKMoI7SLzNZSKBwXmGqkQySFLYhBdJorjWIcjzgJRg_renPgWZ39y77lDmSLgIoCBA"
# urls = MPDParser(url,verbose=True).pre_process().parse().get_segment_urls()
#
#
#
# def progress_callback(progress: Dict):
#     """
#     Progress dict contains:
#     - type: "audio" or "video"
#     - total: total number of segments
#     - current: current segment number
#     - percentage: download progress percentage
#     - segment_num: current segment number being processed
#     - success: whether the current segment was downloaded successfully
#     - failed_segments: list of failed segment numbers
#     - timestamp: current UTC timestamp
#     """
#     return
#     if progress["success"]:
#         debugger.debug(
#             f"Progress: {progress['type']} - {progress['percentage']:.2f}% "
#             f"({progress['current']}/{progress['total']}) "
#             f"Segment {progress['segment_num']}"
#         )
#     else:
#         debugger.warning(
#             f"Failed to download {progress['type']} segment {progress['segment_num']}"
#         )
#
# # Initialize downloader with inline progress
# downloader = DownloaderV3(
#     tmp_dir="C:\\Users\\Akshit\\AppData\\Local\\Temp\\nullaberozgar",
#     out_dir="final_output\\nullaberozgar",
#     verbose=False,  # Set to True for detailed logging
#     progress_callback=progress_callback,
#     max_workers=12,
#     audio_dir="audio",
#     video_dir="video",
# )
#
#
# results = downloader.download_all(urls)
#
#
#
# # Process results
# for media_type, result in results.items():
#     debugger.info(f"\n{media_type.upper()} Download Summary:")
#     debugger.info(f"Init file: {result.init_file}")
#     debugger.info(f"Segments directory: {result.segments_dir}")
#     debugger.info(f"Total segments: {result.total_segments}")
#     debugger.info(f"Successfully downloaded: {result.successful_segments}")
#     debugger.info(f"Failed segments: {result.failed_segments}")
#     SysFunc.concatenate_mp4_segments(str(result.segments_dir),output_filename=f"{media_type.upper()}.mp4",cleanup=True)
#     results[media_type]["encoded-file"]