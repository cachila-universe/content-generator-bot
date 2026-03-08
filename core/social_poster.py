"""
Social media auto-poster — publishes content to Twitter, Instagram, and TikTok.

Supported platforms:
  • Twitter/X   — via Tweepy (full API automation)
  • Instagram   — via Instagram Graph API (Business/Creator accounts)
  • TikTok      — via TikTok Content Posting API

Each platform requires its own API credentials in config/settings.yaml
under the `social` key.
"""

import os
import re
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
#  Twitter / X  (via Tweepy v2)
# ═══════════════════════════════════════════════════════════════════════════
class TwitterPoster:
    """Post tweets and upload videos to Twitter/X."""

    def __init__(self, config: dict):
        """
        config keys (from settings.yaml → social.twitter):
          api_key, api_secret, access_token, access_token_secret, bearer_token
        """
        required = ["api_key", "api_secret", "access_token", "access_token_secret"]
        self.enabled = all(config.get(k, "").strip() for k in required)
        if not self.enabled:
            logger.info("Twitter poster disabled — missing credentials (need api_key, api_secret, access_token, access_token_secret)")
            return

        try:
            import tweepy

            # v1.1 auth (needed for media upload)
            auth = tweepy.OAuth1UserHandler(
                config["api_key"],
                config["api_secret"],
                config["access_token"],
                config["access_token_secret"],
            )
            self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)

            # v2 client (for tweet creation)
            self.client = tweepy.Client(
                bearer_token=config.get("bearer_token", ""),
                consumer_key=config["api_key"],
                consumer_secret=config["api_secret"],
                access_token=config["access_token"],
                access_token_secret=config["access_token_secret"],
                wait_on_rate_limit=True,
            )
            logger.info("Twitter poster initialised ✓")
        except ImportError:
            logger.error("tweepy not installed — run: pip install tweepy")
            self.enabled = False
        except Exception as exc:
            logger.error("Twitter init failed: %s", exc)
            self.enabled = False

    def post_article(self, article: dict) -> str | None:
        """Tweet an article link with title + hashtags."""
        if not self.enabled:
            return None

        title = article.get("title", "")
        url = article.get("url", "")
        niche = article.get("niche_id", "tech")

        hashtags = _make_hashtags(niche, title)
        tweet_text = f"📝 New article: {title}\n\n{url}\n\n{hashtags}"

        # Twitter char limit = 280; trim if needed
        if len(tweet_text) > 280:
            max_title = 280 - len(url) - len(hashtags) - 30
            tweet_text = f"📝 {title[:max_title]}…\n\n{url}\n\n{hashtags}"

        try:
            response = self.client.create_tweet(text=tweet_text, user_auth=True)
            tweet_id = response.data["id"]
            logger.info("Tweet posted: %s", tweet_id)
            return tweet_id
        except Exception as exc:
            logger.error("Tweet failed: %s", exc)
            return None

    def post_video(self, video_path: Path, caption: str) -> str | None:
        """Upload a video and tweet it with a caption."""
        if not self.enabled:
            return None

        if not video_path.exists():
            logger.error("Video file not found: %s", video_path)
            return None

        try:
            # Upload via v1.1 (chunked for videos)
            media = self.api_v1.media_upload(
                filename=str(video_path),
                media_category="tweet_video",
            )

            # Wait for processing
            _wait_for_media(self.api_v1, media.media_id)

            # Tweet with media
            if len(caption) > 280:
                caption = caption[:277] + "…"

            response = self.client.create_tweet(
                text=caption,
                media_ids=[media.media_id],
                user_auth=True,
            )
            tweet_id = response.data["id"]
            logger.info("Video tweet posted: %s", tweet_id)
            return tweet_id
        except Exception as exc:
            logger.error("Video tweet failed: %s", exc)
            return None


def _wait_for_media(api, media_id, max_wait=120):
    """Poll Twitter until media processing finishes."""
    import tweepy

    elapsed = 0
    while elapsed < max_wait:
        status = api.get_media_upload_status(media_id)
        state = status.processing_info.get("state", "succeeded")
        if state == "succeeded":
            return
        if state == "failed":
            raise Exception("Twitter media processing failed")
        wait = status.processing_info.get("check_after_secs", 5)
        time.sleep(wait)
        elapsed += wait


# ═══════════════════════════════════════════════════════════════════════════
#  Instagram Reels  (via Instagram Graph API)
# ═══════════════════════════════════════════════════════════════════════════
class InstagramPoster:
    """
    Post Reels to Instagram via the Graph API.

    Requirements:
      • Instagram Business or Creator account linked to a Facebook Page
      • Facebook App with instagram_content_publish permission
      • Video must be hosted at a public URL (upload to your server first)
    """

    GRAPH_URL = "https://graph.facebook.com/v21.0"

    def __init__(self, config: dict):
        """
        config keys (from settings.yaml → social.instagram):
          access_token, ig_user_id
        """
        self.access_token = (config.get("access_token") or "").strip()
        self.ig_user_id = (config.get("ig_user_id") or "").strip()
        self.enabled = bool(self.access_token and self.ig_user_id)

        if not self.enabled:
            logger.info("Instagram poster disabled — no credentials configured (need access_token + ig_user_id)")
        else:
            logger.info("Instagram poster initialised ✓")

    def post_reel(self, video_url: str, caption: str) -> str | None:
        """
        Publish a Reel.

        video_url: Public URL where the .mp4 file is hosted
        caption:   Post caption with hashtags
        """
        if not self.enabled:
            return None

        try:
            import httpx

            # Step 1: Create media container
            resp = httpx.post(
                f"{self.GRAPH_URL}/{self.ig_user_id}/media",
                params={
                    "media_type": "REELS",
                    "video_url": video_url,
                    "caption": caption,
                    "access_token": self.access_token,
                },
                timeout=60,
            )
            resp.raise_for_status()
            container_id = resp.json()["id"]
            logger.info("IG container created: %s", container_id)

            # Step 2: Wait for processing
            self._wait_for_container(container_id)

            # Step 3: Publish
            pub_resp = httpx.post(
                f"{self.GRAPH_URL}/{self.ig_user_id}/media_publish",
                params={
                    "creation_id": container_id,
                    "access_token": self.access_token,
                },
                timeout=60,
            )
            pub_resp.raise_for_status()
            media_id = pub_resp.json()["id"]
            logger.info("Instagram Reel published: %s", media_id)
            return media_id

        except Exception as exc:
            logger.error("Instagram Reel failed: %s", exc)
            return None

    def _wait_for_container(self, container_id: str, max_wait: int = 300):
        """Poll until the media container is ready."""
        import httpx

        elapsed = 0
        while elapsed < max_wait:
            resp = httpx.get(
                f"{self.GRAPH_URL}/{container_id}",
                params={
                    "fields": "status_code",
                    "access_token": self.access_token,
                },
                timeout=30,
            )
            status = resp.json().get("status_code", "")
            if status == "FINISHED":
                return
            if status == "ERROR":
                raise Exception(f"IG container error: {resp.json()}")
            time.sleep(10)
            elapsed += 10
        raise TimeoutError("Instagram media processing timed out")


# ═══════════════════════════════════════════════════════════════════════════
#  TikTok  (via Content Posting API)
# ═══════════════════════════════════════════════════════════════════════════
class TikTokPoster:
    """
    Post videos to TikTok via the Content Posting API.

    Requirements:
      • TikTok Developer account with approved app
      • OAuth access token with video.publish scope
      • Video must be hosted at a public URL

    Token lifecycle:
      • access_token expires every 24 hours
      • refresh_token is valid for 365 days
      • Call refresh_access_token() daily via the scheduler
    """

    API_URL = "https://open.tiktokapis.com/v2"

    def __init__(self, config: dict):
        """
        config keys (from settings.yaml → social.tiktok):
          client_key, client_secret, access_token, refresh_token
        """
        self.access_token = (config.get("access_token") or "").strip()
        self.refresh_token = (config.get("refresh_token") or "").strip()
        self.client_key = (config.get("client_key") or "").strip()
        self.client_secret = (config.get("client_secret") or "").strip()
        self.enabled = bool(self.access_token)

        if not self.enabled:
            logger.info("TikTok poster disabled — no access token configured")
        else:
            logger.info("TikTok poster initialised ✓")

    def refresh_access_token(self) -> bool:
        """
        Use the refresh_token to get a new access_token.
        Call this daily (access tokens expire every 24 hours).

        Returns True on success. Updates self.access_token in-place.
        """
        if not self.refresh_token or not self.client_key:
            logger.warning("TikTok: cannot refresh — missing refresh_token or client_key")
            return False

        try:
            import httpx

            resp = httpx.post(
                f"{self.API_URL}/oauth/token/",
                data={
                    "client_key": self.client_key,
                    "client_secret": self.client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            new_token = data.get("access_token", "")
            new_refresh = data.get("refresh_token", "")

            if new_token:
                self.access_token = new_token
                if new_refresh:
                    self.refresh_token = new_refresh
                logger.info("TikTok access token refreshed successfully")
                return True
            else:
                logger.error("TikTok token refresh returned no access_token: %s", data)
                return False

        except Exception as exc:
            logger.error("TikTok token refresh failed: %s", exc)
            return False

    def post_video(self, video_url: str, caption: str) -> str | None:
        """
        Publish a video to TikTok.

        video_url: Public URL where the .mp4 file is hosted
        caption:   Video description with hashtags
        """
        if not self.enabled:
            return None

        try:
            import httpx

            # Step 1: Init upload
            resp = httpx.post(
                f"{self.API_URL}/post/publish/video/init/",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json; charset=UTF-8",
                },
                json={
                    "post_info": {
                        "title": caption[:150],
                        "privacy_level": "PUBLIC_TO_EVERYONE",
                        "disable_duet": False,
                        "disable_comment": False,
                        "disable_stitch": False,
                    },
                    "source_info": {
                        "source": "PULL_FROM_URL",
                        "video_url": video_url,
                    },
                },
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json().get("data", {})
            publish_id = data.get("publish_id", "")
            logger.info("TikTok publish initiated: %s", publish_id)
            return publish_id

        except Exception as exc:
            logger.error("TikTok post failed: %s", exc)
            return None


# ═══════════════════════════════════════════════════════════════════════════
#  Unified poster — one function to post everywhere
# ═══════════════════════════════════════════════════════════════════════════
class SocialPoster:
    """Unified interface to post content across all platforms."""

    def __init__(self, settings: dict):
        """
        settings: The full settings.yaml dict. Reads from `social` key.
        """
        social = settings.get("social", {})
        self.twitter = TwitterPoster(social.get("twitter", {}))
        self.instagram = InstagramPoster(social.get("instagram", {}))
        self.tiktok = TikTokPoster(social.get("tiktok", {}))

    def post_article_everywhere(self, article: dict) -> dict:
        """Post an article link to all text-based platforms (Twitter)."""
        results = {}

        if self.twitter.enabled:
            results["twitter"] = self.twitter.post_article(article)

        return results

    def post_video_everywhere(
        self,
        video_path: Path,
        video_url: str,
        caption: str,
        article: dict | None = None,
    ) -> dict:
        """
        Post a video to all video platforms.

        video_path: Local path to .mp4 (for Twitter upload)
        video_url:  Public URL of the .mp4 (for IG/TikTok)
        caption:    Caption/description text
        """
        results = {}
        niche = article.get("niche_id", "tech") if article else "tech"
        hashtags = _make_hashtags(niche, caption)
        full_caption = f"{caption}\n\n{hashtags}"

        # Twitter: upload from local file
        if self.twitter.enabled:
            results["twitter"] = self.twitter.post_video(video_path, full_caption[:280])

        # Instagram Reels: needs public URL
        if self.instagram.enabled and video_url:
            results["instagram"] = self.instagram.post_reel(video_url, full_caption[:2200])

        # TikTok: needs public URL
        if self.tiktok.enabled and video_url:
            results["tiktok"] = self.tiktok.post_video(video_url, full_caption[:2200])

        return results

    @property
    def active_platforms(self) -> list[str]:
        """Return names of platforms that are configured."""
        platforms = []
        if self.twitter.enabled:
            platforms.append("twitter")
        if self.instagram.enabled:
            platforms.append("instagram")
        if self.tiktok.enabled:
            platforms.append("tiktok")
        return platforms


# ═══════════════════════════════════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════════════════════════════════
NICHE_HASHTAGS = {
    "ai_tools": "#AI #AITools #ArtificialIntelligence #Productivity #Tech",
    "personal_finance": "#PersonalFinance #Money #Investing #Budget #Finance",
    "health_biohacking": "#Health #Biohacking #Wellness #Longevity #HealthTech",
    "home_tech": "#SmartHome #HomeTech #IoT #Gadgets #HomeAutomation",
    "travel": "#Travel #TravelTips #TravelTech #DigitalNomad #Explore",
    "pet_care": "#Pets #PetCare #Dogs #Cats #PetHealth",
    "fitness_wellness": "#Fitness #Wellness #Workout #GymLife #HealthyLiving",
    "remote_work": "#RemoteWork #WFH #Productivity #DigitalNomad #WorkFromHome",
}


def _make_hashtags(niche: str, text: str = "") -> str:
    """Generate relevant hashtags for a niche."""
    base = NICHE_HASHTAGS.get(niche, "#TechLife #Tips")
    return f"{base} #TechLifeInsights"
