import os
import json
import smtplib
import requests
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import re

class InternshipMonitor:
    def __init__(self):
        self.github_url = "https://raw.githubusercontent.com/vanshb03/Summer2026-Internships/main/README.md"
        self.data_file = "internships_data.json"
        
        # Email configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.notify_email = os.getenv('NOTIFY_EMAIL')
        
    def get_readme_content(self):
        """Fetch README.md content directly"""
        try:
            response = requests.get(self.github_url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching README: {e}")
            return None
    
    def parse_internships_table(self, content):
        """Parse the markdown table to extract internship data"""
        internships = []
        
        # Find the table section
        table_start = content.find('| Company | Role | Location | Application/Link | Date Posted |')
        table_end = content.find('<!-- Please leave a one line gap between this and the table TABLE_END')
        
        if table_start == -1 or table_end == -1:
            print("Could not find table boundaries")
            return internships
        
        table_section = content[table_start:table_end]
        lines = table_section.split('\n')
        
        for line in lines[2:]:  # Skip header and separator
            line = line.strip()
            if not line or line.startswith('|---') or '🔒' in line:
                continue
                
            # Parse table row
            parts = [part.strip() for part in line.split('|')]
            if len(parts) >= 6:
                company = parts[1].strip()
                role = parts[2].strip()
                location = parts[3].strip()
                application_link = parts[4].strip()
                date_posted = parts[5].strip()
                
                # Skip empty rows and continuation rows (↳)
                if not company or company == '↳':
                    continue
                
                # Extract actual URL from markdown link
                url_match = re.search(r'href="([^"]+)"', application_link)
                apply_url = url_match.group(1) if url_match else ""
                
                # Create unique identifier
                internship_id = hashlib.md5(f"{company}{role}{location}".encode()).hexdigest()
                
                internship = {
                    'id': internship_id,
                    'company': company,
                    'role': role,
                    'location': location,
                    'apply_url': apply_url,
                    'date_posted': date_posted,
                    'found_at': datetime.now().isoformat()
                }
                
                internships.append(internship)
        
        return internships
    
    def load_previous_data(self):
        """Load previously stored internship data"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading previous data: {e}")
            return []
    
    def save_current_data(self, internships):
        """Save current internship data"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(internships, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def find_new_internships(self, current_internships, previous_internships):
        """Compare current vs previous to find new internships"""
        previous_ids = {internship['id'] for internship in previous_internships}
        new_internships = [
            internship for internship in current_internships 
            if internship['id'] not in previous_ids
        ]
        return new_internships
    
    def send_email_alert(self, new_internships):
        """Send email notification for new internships"""
        if not self.email_user or not self.email_password or not self.notify_email:
            print("Email credentials not configured")
            return False
        
        try:
            subject = f"🚨 {len(new_internships)} New Summer 2026 Internship(s) Available!"
            html_body = self.create_email_html(new_internships)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_user
            msg['To'] = self.notify_email
            
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            print(f"Email sent successfully for {len(new_internships)} new internships")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def create_email_html(self, internships):
        """Create HTML email content"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .internship {{ border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 5px; }}
                .company {{ font-size: 18px; font-weight: bold; color: #2c3e50; }}
                .role {{ font-size: 16px; color: #34495e; margin: 5px 0; }}
                .location {{ color: #7f8c8d; margin: 5px 0; }}
                .apply-btn {{ 
                    background-color: #3498db; color: white; padding: 10px 20px; 
                    text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🎉 New Summer 2026 Internships Alert!</h2>
                <p>Found {len(internships)} new internship opening(s).</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
        """
        
        for internship in internships:
            html += f"""
            <div class="internship">
                <div class="company">{internship['company']}</div>
                <div class="role"><strong>Role:</strong> {internship['role']}</div>
                <div class="location"><strong>Location:</strong> {internship['location']}</div>
                <div><strong>Date Posted:</strong> {internship['date_posted']}</div>
                <a href="{internship['apply_url']}" class="apply-btn">Apply Now</a>
            </div>
            """
        
        html += """
            <div style="margin-top: 30px; font-size: 12px; color: #7f8c8d;">
                <p>Repository: <a href="https://github.com/vanshb03/Summer2026-Internships">Summer2026-Internships</a></p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def run(self):
        """Main execution function"""
        print("Starting internship check...")
        
        # Get current README content
        content = self.get_readme_content()
        if not content:
            print("Failed to fetch README content")
            return
        
        # Parse current internships
        current_internships = self.parse_internships_table(content)
        print(f"Found {len(current_internships)} total internships")
        
        # Load previous data
        previous_internships = self.load_previous_data()
        print(f"Previous data had {len(previous_internships)} internships")
        
        # Find new internships
        new_internships = self.find_new_internships(current_internships, previous_internships)
        
        if new_internships:
            print(f"Found {len(new_internships)} new internships!")
            for internship in new_internships:
                print(f"- {internship['company']}: {internship['role']}")
            
            # Send email alert
            self.send_email_alert(new_internships)
        else:
            print("No new internships found")
        
        # Save current data
        self.save_current_data(current_internships)
        print("Data saved successfully")

if __name__ == "__main__":
    monitor = InternshipMonitor()
    monitor.run()