"""
Gmail Availability Checker & Brand Suggester
==========================================

Quick tool to suggest available professional Gmail addresses
"""

def suggest_gmail_options(name="helm"):
    """Suggest available Gmail options"""
    
    base_names = [
        "helm.ai.tech",
        "helm.ai.platform", 
        "helm.ai.systems",
        "helm.ai.solutions",
        "helm.ai.corp",
        "helm.ai.enterprise",
        "helm.ai.startup",
        "helm.ai.founder",
        "helm.aitech",
        "helm.aisystems",
        "helm.aitech",
        "helm.aicorp",
        "helmai.tech",
        "helmai.platform",
        "helmai.systems",
        "helmai.solutions"
    ]
    
    # Add your name variations (replace with your actual name)
    your_name = "yourname"  # Replace with your name
    name_variations = [
        f"{your_name}.helm.ai",
        f"{your_name}.helmai",
        f"helm.ai.{your_name}",
        f"helmai.{your_name}",
        f"{your_name}.aitech",
        f"{your_name}.aisystems"
    ]
    
    all_options = base_names + name_variations
    
    print("📧 Professional Gmail Options to Try:")
    print("=" * 50)
    
    for i, option in enumerate(all_options, 1):
        print(f"{i:2d}. {option}@gmail.com")
    
    print("\n🎯 Top 5 Recommendations:")
    print("=" * 30)
    
    top_recommendations = [
        "helm.ai.tech@gmail.com",
        "helm.ai.platform@gmail.com", 
        "helm.ai.systems@gmail.com",
        "helm.aitech@gmail.com",
        "helmai.tech@gmail.com"
    ]
    
    for i, email in enumerate(top_recommendations, 1):
        print(f"{i}. {email}")
    
    print("\n🏢 Matching Company Names:")
    print("=" * 35)
    
    company_mappings = {
        "helm.ai.tech": "Helm AI Tech",
        "helm.ai.platform": "Helm AI Platform", 
        "helm.ai.systems": "Helm AI Systems",
        "helm.aitech": "Helm AI Tech",
        "helmai.tech": "Helm AI Tech"
    }
    
    for email, company in company_mappings.items():
        print(f"📧 {email}@gmail.com")
        print(f"🏢 {company}")
        print(f"🌐 {company.lower().replace(' ', '')}.ai")
        print()

def check_availability_tips():
    """Tips for checking Gmail availability"""
    
    print("🔍 How to Check Availability:")
    print("=" * 40)
    print("1. Go to gmail.com")
    print("2. Click 'Create account'")
    print("3. Try each username")
    print("4. Gmail will tell you if it's available")
    print()
    
    print("💡 Pro Tips:")
    print("=" * 20)
    print("• Use periods (.) to separate words")
    print("• Avoid numbers if possible")
    print("• Keep it under 30 characters")
    print("• Make it easy to spell and say")
    print("• Professional appearance matters")

# Run the suggestions
if __name__ == "__main__":
    suggest_gmail_options()
    print()
    check_availability_tips()
    
    print("\n🚀 Next Steps:")
    print("=" * 20)
    print("1. Try the top 5 recommendations")
    print("2. Pick the first available one")
    print("3. Set up professional signature")
    print("4. Update LinkedIn profile")
    print("5. Start outreach tomorrow!")
    print()
    print("📊 Remember: The exact email doesn't matter as much as")
    print("   the execution and value you provide!")
    print("   Focus on getting meetings and building relationships!")
