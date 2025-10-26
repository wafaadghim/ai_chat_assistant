"""
Test module for AI Chat Assistant.
"""

import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_chat_assistant import ChatBot, Conversation


def test_chatbot_greeting():
    """Test chatbot greeting functionality."""
    bot = ChatBot(name="TestBot")
    response = bot.process_message("Bonjour")
    assert "Bonjour" in response
    assert "TestBot" in response
    print("✓ Test greeting passed")


def test_chatbot_time():
    """Test chatbot time functionality."""
    bot = ChatBot(name="TestBot")
    response = bot.process_message("Quelle heure?")
    assert "actuellement" in response
    print("✓ Test time passed")


def test_chatbot_date():
    """Test chatbot date functionality."""
    bot = ChatBot(name="TestBot")
    response = bot.process_message("Quelle est la date?")
    assert "Nous sommes" in response
    print("✓ Test date passed")


def test_conversation_history():
    """Test conversation history functionality."""
    bot = ChatBot(name="TestBot")
    bot.process_message("Bonjour")
    bot.process_message("Comment vas-tu?")
    
    history = bot.get_conversation_history()
    assert len(history) == 2
    assert history[0]["user"] == "Bonjour"
    assert history[1]["user"] == "Comment vas-tu?"
    print("✓ Test conversation history passed")


def test_clear_history():
    """Test clearing conversation history."""
    bot = ChatBot(name="TestBot")
    bot.process_message("Test message")
    bot.clear_history()
    
    history = bot.get_conversation_history()
    assert len(history) == 0
    print("✓ Test clear history passed")


def test_conversation_storage():
    """Test conversation storage functionality."""
    import tempfile
    import os
    
    # Create temporary file for testing
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_file.close()
    
    try:
        conv = Conversation(storage_path=temp_file.name)
        test_data = [
            {"timestamp": "2025-10-26T00:00:00", "user": "Test", "bot": "Response"}
        ]
        conv.save_conversation(test_data)
        
        # Create new instance to test loading
        conv2 = Conversation(storage_path=temp_file.name)
        all_convs = conv2.get_all_conversations()
        assert len(all_convs) >= 1
        print("✓ Test conversation storage passed")
    finally:
        # Clean up
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("Running AI Chat Assistant Tests")
    print("=" * 50 + "\n")
    
    try:
        test_chatbot_greeting()
        test_chatbot_time()
        test_chatbot_date()
        test_conversation_history()
        test_clear_history()
        test_conversation_storage()
        
        print("\n" + "=" * 50)
        print("All tests passed! ✓")
        print("=" * 50 + "\n")
        return True
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}\n")
        return False
    except Exception as e:
        print(f"\n✗ Error running tests: {e}\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
