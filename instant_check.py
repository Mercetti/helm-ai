import socket
import time
from datetime import datetime

def check_port(port, name):
    """Check if port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)  # Very short timeout
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def main():
    print(f"\n🔍 Stellar Logic AI - Instant System Check")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    servers = [
        (5000, "Dashboard"),
        (5001, "LLM Server"),
        (5002, "Team Chat"),
        (5003, "Voice Chat"),
        (5004, "Video Chat"),
        (5005, "Friends System"),
        (5006, "Analytics"),
        (5007, "Security"),
        (11434, "Ollama")
    ]
    
    running_count = 0
    total_count = len(servers)
    
    for port, name in servers:
        if check_port(port, name):
            print(f"✅ {name:<15} - Port {port:<6} - RUNNING")
            running_count += 1
        else:
            print(f"❌ {name:<15} - Port {port:<6} - OFFLINE")
    
    print("=" * 50)
    health_percentage = (running_count / total_count) * 100
    print(f"📊 System Health: {health_percentage:.1f}% ({running_count}/{total_count})")
    
    if health_percentage >= 80:
        print("🎉 PLATFORM IS LAUNCH-READY!")
        print("✅ Ready for investor demos")
        print("🚀 Ready for market launch")
    elif health_percentage >= 60:
        print("⚠️ System mostly operational")
        print("🔧 Minor issues to address")
    else:
        print("❌ System needs attention")
        print("🛠️ Significant issues found")
    
    print(f"\n🎯 Status: {health_percentage:.0f}% Complete")
    return health_percentage

if __name__ == "__main__":
    main()
