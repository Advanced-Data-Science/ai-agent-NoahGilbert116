import os
import sys
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

class SpotifyAPITester:
    def __init__(self):
        self.results = {
            "environment": False,
            "authentication": False,
            "api_connection": False,
            "playlist_access": False,
            "search_functionality": False
        }
        self.sp = None
        
    def print_header(self, message):
        print(f"\n{'='*50}")
        print(f"🔧 {message}")
        print(f"{'='*50}")
        
    def print_success(self, message):
        print(f"✅ {message}")
        
    def print_error(self, message):
        print(f"❌ {message}")
        
    def print_info(self, message):
        print(f"ℹ️  {message}")

    def test_environment_variables(self):
        """Test if environment variables are properly set"""
        self.print_header("Testing Environment Variables")
        
        load_dotenv()
        
        # Try both naming conventions
        client_id = os.getenv("CLIENT_ID") or os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET") or os.getenv("SPOTIFY_CLIENT_SECRET")
        
        print(f"CLIENT_ID: {'✅ Found' if client_id else '❌ Missing'}")
        print(f"CLIENT_SECRET: {'✅ Found' if client_secret else '❌ Missing'}")
        
        if client_id and client_secret:
            self.print_success("All environment variables are set!")
            self.results["environment"] = True
            return True
        else:
            self.print_error("Missing environment variables!")
            self.print_info("Please check your .env file")
            return False

    def test_authentication(self):
        """Test Spotify API authentication"""
        self.print_header("Testing Authentication")
        
        try:
            client_id = os.getenv("CLIENT_ID") or os.getenv("SPOTIFY_CLIENT_ID")
            client_secret = os.getenv("CLIENT_SECRET") or os.getenv("SPOTIFY_CLIENT_SECRET")
            
            auth_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            
            # Create Spotipy client with shorter timeout for quick testing
            self.sp = spotipy.Spotify(
                auth_manager=auth_manager,
                requests_timeout=10,
                retries=1
            )
            
            self.print_success("Authentication successful!")
            self.results["authentication"] = True
            return True
            
        except Exception as e:
            self.print_error(f"Authentication failed: {e}")
            return False

    def test_api_connection(self):
        """Test basic API connectivity with a simple search"""
        self.print_header("Testing API Connection")
        
        try:
            # Test with a simple search query
            results = self.sp.search(q='artist:Ed Sheeran', type='track', limit=1)
            
            if results and 'tracks' in results:
                track = results['tracks']['items'][0]
                self.print_success("API connection successful!")
                print(f"   Test track: {track['name']}")
                print(f"   Artist: {track['artists'][0]['name']}")
                print(f"   Duration: {track['duration_ms']}ms")
                
                self.results["api_connection"] = True
                return True
            else:
                self.print_error("No results returned from API")
                return False
                
        except Exception as e:
            self.print_error(f"API connection test failed: {e}")
            return False

    def test_playlist_access(self):
        """Test accessing playlist data"""
        self.print_header("Testing Playlist Access")
        
        try:
            # Test with Spotify's Global Top 50 playlist
            playlist_id = '37i9dQZEVXbMDoHDwVN2tF'  # Global Top 50
            playlist = self.sp.playlist(playlist_id)
            
            if playlist:
                self.print_success("Playlist access successful!")
                print(f"   Playlist: {playlist['name']}")
                print(f"   Description: {playlist.get('description', 'No description')}")
                print(f"   Followers: {playlist['followers']['total']:,}")
                print(f"   Tracks: {playlist['tracks']['total']}")
                print(f"   Public: {playlist['public']}")
                
                # Test getting a few tracks
                tracks = self.sp.playlist_tracks(playlist_id, limit=3)
                if tracks and 'items' in tracks:
                    print(f"   Sample tracks:")
                    for i, item in enumerate(tracks['items'][:3]):
                        track = item['track']
                        print(f"     {i+1}. {track['name']} - {track['artists'][0]['name']}")
                
                self.results["playlist_access"] = True
                return True
                
        except Exception as e:
            self.print_error(f"Playlist access test failed: {e}")
            return False

    def test_search_functionality(self):
        """Test search functionality with different types"""
        self.print_header("Testing Search Functionality")
        
        try:
            search_queries = [
                {"q": "Dua Lipa", "type": "artist"},
                {"q": "Blinding Lights", "type": "track"},
                {"q": "Today's Top Hits", "type": "playlist"},
                {"q": "Future Nostalgia", "type": "album"}
            ]
            
            for query in search_queries:
                results = self.sp.search(
                    q=query["q"], 
                    type=query["type"], 
                    limit=1
                )
                
                if results and f"{query['type']}s" in results:
                    items = results[f"{query['type']}s"]['items']
                    if items:
                        item = items[0]
                        if query["type"] == "artist":
                            print(f"   Artist: {item['name']} - {item['followers']['total']:,} followers")
                        elif query["type"] == "track":
                            print(f"   Track: {item['name']} - {item['artists'][0]['name']}")
                        elif query["type"] == "playlist":
                            print(f"   Playlist: {item['name']} - {item['owner']['display_name']}")
                        elif query["type"] == "album":
                            print(f"   Album: {item['name']} - {item['artists'][0]['name']}")
            
            self.print_success("Search functionality working!")
            self.results["search_functionality"] = True
            return True
            
        except Exception as e:
            self.print_error(f"Search functionality test failed: {e}")
            return False

    def test_audio_features(self):
        """Test audio features endpoint"""
        self.print_header("Testing Audio Features")
        
        try:
            # Get a popular track ID first
            results = self.sp.search(q='track:Blinding Lights artist:The Weeknd', type='track', limit=1)
            if results and results['tracks']['items']:
                track_id = results['tracks']['items'][0]['id']
                
                # Get audio features
                features = self.sp.audio_features([track_id])[0]
                
                if features:
                    self.print_success("Audio features access successful!")
                    print(f"   Danceability: {features['danceability']:.2f}")
                    print(f"   Energy: {features['energy']:.2f}")
                    print(f"   Valence: {features['valence']:.2f}")
                    print(f"   Tempo: {features['tempo']} BPM")
                    print(f"   Key: {features['key']}")
                    print(f"   Mode: {'Major' if features['mode'] == 1 else 'Minor'}")
                    
                    return True
                    
        except Exception as e:
            self.print_error(f"Audio features test failed: {e}")
            return False

    def run_all_tests(self):
        """Run all tests and provide summary"""
        self.print_header("Starting Spotify API Test Suite")
        
        tests = [
            self.test_environment_variables,
            self.test_authentication,
            self.test_api_connection,
            self.test_playlist_access,
            self.test_search_functionality,
            self.test_audio_features
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.print_error(f"Test {test.__name__} crashed: {e}")
        
        self.print_summary()

    def print_summary(self):
        """Print final test summary"""
        self.print_header("Test Summary")
        
        passed = sum(self.results.values())
        total = len(self.results)
        
        for test_name, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name.replace('_', ' ').title():<20} {status}")
        
        print(f"\n📊 Overall Result: {passed}/{total} tests passed")
        
        if passed == total:
            self.print_success("All tests passed! Your Spotify API setup is working correctly.")
            print("\n🎉 You're ready to use the Spotify Agent!")
        else:
            self.print_error("Some tests failed. Please check your setup.")
            print("\n🔧 Troubleshooting tips:")
            print("   • Verify your Client ID and Secret in .env file")
            print("   • Check your internet connection")
            print("   • Ensure your Spotify app is active in Developer Dashboard")
            print("   • Verify no typos in environment variable names")

def quick_test():
    """Simple one-line test for quick verification"""
    print("🚀 Quick Spotify API Test")
    print("=" * 30)
    
    try:
        load_dotenv()
        client_id = os.getenv("CLIENT_ID") or os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET") or os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            print("❌ Missing credentials in .env file")
            return False
            
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(auth_manager=auth_manager, requests_timeout=10)
        
        # Quick test
        results = sp.search(q='artist:Spotify', type='playlist', limit=1)
        if results:
            print("✅ Spotify API is working!")
            return True
        else:
            print("❌ API returned no results")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_test()
    else:
        tester = SpotifyAPITester()
        tester.run_all_tests()
