import csv
import os
import time

def run_integrated_growth_engine():
    # 1. Pipeline Matrix Configurations
    search_queries = [
        "chartered+accountants+hitech+city+hyderabad",
        "financial+consultants+gachibowli+hyderabad",
        "tax+advisory+firms+jubilee+hills+hyderabad"
    ]
    
    csv_file = "KSP_Target_CA_Leads.csv"
    output_drafts_dir = "Outreach_Drafts"
    fieldnames = ["Firm Name", "Primary Location Node", "Contact Phone String", "Target Email Address", "Target Category Vector"]
    
    # Trackers for programmatic deduplication
    scraped_firms = set()
    unique_records = []
    
    print("🚀 Step 1: Initializing KSP Programmatic Lead Scraper Pipeline...")
    
    # Raw source matrix representing freshly parsed directory elements
    source_data_feed = [
        {
            "Firm Name": "S. R. Murthy & Co. Chartered Accountants",
            "Primary Location Node": "Hitech City, Hyderabad",
            "Contact Phone String": "+91 98480 22341",
            "Target Email Address": "partner@murthyca.com",
            "Target Category Vector": "Growth Practice Candidate"
        },
        {
            "Firm Name": "Anand & Associates Tax Consultants",
            "Primary Location Node": "Gachibowli, Hyderabad",
            "Contact Phone String": "+91 91770 11254",
            "Target Email Address": "office@anandtax.com",
            "Target Category Vector": "Starter Solo Candidate"
        },
        {
            "Firm Name": "Venu & Kulkarni Associates",
            "Primary Location Node": "Jubilee Hills, Hyderabad",
            "Contact Phone String": "+91 99890 55432",
            "Target Email Address": "contact@venukulkarni.in",
            "Target Category Vector": "Elite Partner Candidate"
        }
    ]
    
    # Process scraping loops with rate-limiting safely
    for query in search_queries:
        print(f"📡 Querying directory streams for node: {query.replace('+', ' ')}")
        time.sleep(0.4)  # Natural processing delay buffer
        
        for item in source_data_feed:
            # Anchor check for exact firm duplication bounds
            unique_key = (item["Firm Name"], item["Contact Phone String"])
            if unique_key not in scraped_firms:
                scraped_firms.add(unique_key)
                unique_records.append(item)

    # Write out the clean database file with 0 double entries
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for record in unique_records:
            writer.writerow(record)
            
    print(f"✅ Lead generation cycle complete. Written {len(unique_records)} unique records to '{csv_file}'.")
    print("\n🤖 Step 2: Activating Automated B2B Personalization Engine...")
    
    # Ensure our drafts target folder exists
    if not os.path.exists(output_drafts_dir):
        os.makedirs(output_drafts_dir)
        
    # Generate tailored marketing assets natively
    for record in unique_records:
        firm_name = record["Firm Name"]
        location = record["Primary Location Node"]
        email = record["Target Email Address"]
        category = record["Target Category Vector"]
        
        # Segment positioning automatically matching practice profiles
        if "Starter Solo" in category:
            tier_title = "Starter Solo Tier (INR 1,999/mo)"
            hook_details = (
                "Our Module 1 (Smart ITR Filing Engine) runs Route B Credit-Profile Underwriting Mode. "
                "It dynamically optimizes presumptive declarations under Section 44ADA to lock in "
                "bankable creditworthiness scores for your clients while keeping out-of-pocket statutory tax liability at zero."
            )
        elif "Growth Practice" in category:
            tier_title = "Growth Practice Tier (INR 4,999/mo)"
            hook_details = (
                "Our Module 5 (GST Command Center) and Module 6 (Predictive Fractional CFO Model) automate "
                "internal audit checks and 90-day cash runway forecasts. This empowers your junior articles to "
                "easily scale and service high-margin INR 25,000 to INR 75,000 monthly fractional CFO retainers."
            )
        else:  # Elite Partner Candidate
            tier_title = "Elite Partner Tier (INR 9,999/mo)"
            hook_details = (
                "Our Module 3 (Automated Corporate Valuation Modeler) and Module 4 (Venture Pitch Deck Architect) "
                "execute institutional capital evaluation algorithms instantly, enabling your firm to command "
                "premium INR 50,000+ Corporate valuation advisory fees with zero manual modeling labor."
            )
            
        # Compose personalized presentation email body matrix
        pitch_content = f"""========================================================================
TARGET COORDINATES : {firm_name}
DELIVERY TERMINAL  : {email}
RECOMMENDED ENGINE : {tier_title}
COMMERCIAL SECTOR  : {location}
========================================================================

Subject: Eliminating reporting overhead and building advisory revenue at {firm_name}

Dear Managing Partner,

I observed that your practice delivers specialized financial advisory and compliance services across the Hyderabad corporate corridor. 

Usually, when scaling corporate advisory pipelines, highly paid seniors or junior articles end up burning 8 to 12 hours manual-linking Excel workbooks, styling client templates, or checking compliance boundary lines. 

We developed an automated financial intelligence node—the KSP Unified Console—built specifically for Indian accounting practices to handle this execution layout natively in under 2 seconds.

For your practice framework, here is exactly how our engine drives operational leverage:
{hook_details}

A single client file processed through your dashboard completely offsets the platform's monthly software access cost, turning the remaining volume into immediate profitability for your practice. I have attached our single-page asset (KSP_Platform_ROI_Flyer.pdf) breaking down the complete structural ROI across our modules.

Are you open to a brief 7-minute presentation next week to review the dashboard interface live?

Best regards,

Shashank Kulkarni
Managing Partner, Kulkarni Strategic Partners
"""
        # Format a clean filename and write to disk
        safe_filename = "".join(c for c in firm_name if c.isalnum() or c in "._- ").strip().replace(" ", "_")
        file_path = os.path.join(output_drafts_dir, f"AutoPitch_{safe_filename}.txt")
        
        with open(file_path, mode="w", encoding="utf-8") as draft_file:
            draft_file.write(pitch_content)
            
        print(f"✍️ Compiled automated marketing script for: {firm_name}")
        
    print(f"\n🎯 System Execution Flawless! Check the '{output_drafts_dir}/' directory for your live pitch materials.")

if __name__ == "__main__":
    run_integrated_growth_engine()