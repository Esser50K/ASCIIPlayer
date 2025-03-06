import yt_dlp
from urllib.parse import urlparse


def is_youtube_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if hostname is None:
            return False
        hostname = hostname.lower()
        # Check for youtu.be or youtube.com (including subdomains)
        if hostname == "youtu.be":
            return True
        if hostname == "youtube.com" or hostname.endswith(".youtube.com"):
            return True
        return False
    except Exception:
        return False


def find_best_video_quality_url(video_info: dict) -> dict:
    highest_allowed_resolution = 340
    found_formats = {}
    for format in video_info["formats"]:
        if format["vcodec"] != "none":
            codec = format["vcodec"]
            # height because it basically defines resolution. e.g. 640x480 -> 480p
            resolution = format["height"]
            fps = format["fps"]
            found_formats["%s_%s_%s" % (codec, resolution, fps)] = format

    video_formats = [format for format in found_formats.values()
                     if type(format["height"]) is int]
    sorted_formats = sorted(video_formats, key=lambda x: x["height"])
    if sorted_formats[0]["height"] > highest_allowed_resolution:
        raise Exception("no desired resolution found, found resolutions:", list(
            map(lambda x: x["height"], found_formats.values())))

    return sorted_formats[0]


def get_youtube_video_url(yt_url: str):
    options = {}
    ytdl = yt_dlp.YoutubeDL(options)
    info_dict = ytdl.extract_info(yt_url, download=False)
    best_video_format = find_best_video_quality_url(info_dict)

    return best_video_format["url"]
