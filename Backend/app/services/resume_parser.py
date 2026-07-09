import spacy
import PyPDF2
import docx
import re
from typing import List, Dict, Any

class ResumeParser:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except:
            self.nlp = spacy.load("en_core_web_sm")
        
        self.skills_db = self._load_skills_database()
    
    def _load_skills_database(self) -> List[str]:
        """Load skills from database or file"""
        return [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'machine learning', 'deep learning', 'nlp', 'tensorflow', 'pytorch',
            'sql', 'mongodb', 'postgresql', 'mysql', 'aws', 'azure', 'gcp',
            'docker', 'kubernetes', 'git', 'jenkins', 'ci/cd', 'devops',
            'fastapi', 'django', 'flask', 'spring boot', '.net', 'c#', 'c++',
            'html', 'css', 'typescript', 'tailwind', 'bootstrap',
            'excel', 'powerpoint', 'word', 'tableau', 'power bi',
            'agile', 'scrum', 'jira', 'confluence'
        ]
    
    async def parse(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Main parsing function"""
        
        text = self._extract_text(file_path, file_type)
        
        parsed_data = {
            'personal_info': self._extract_personal_info(text),
            'skills': self._extract_skills(text),
            'experience': self._extract_experience(text),
            'education': self._extract_education(text),
            'certifications': self._extract_certifications(text),
            'total_experience_years': self._calculate_total_experience(text),
            'highest_education': self._get_highest_education(text)
        }
        
        return parsed_data
    
    def _extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text from PDF or DOCX"""
        text = ""
        
        if file_type == "pdf":
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        
        elif file_type in ["docx", "doc"]:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        
        return text
    
    def _extract_personal_info(self, text: str) -> Dict[str, str]:
        """Extract name, email, phone, location"""
        info = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        info['email'] = emails[0] if emails else None
        
        # Extract phone
        phone_pattern = r'(\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}'
        phones = re.findall(phone_pattern, text)
        info['phone'] = phones[0] if phones else None
        
        # Extract name using spaCy NER
        doc = self.nlp(text[:2000])
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                info['name'] = ent.text
                break
        
        return info
    
    def _extract_skills(self, text: str) -> List[Dict[str, Any]]:
        """Extract skills from text"""
        found_skills = []
        text_lower = text.lower()
        
        for skill in self.skills_db:
            if skill in text_lower:
                confidence = 0.8
                # Check for multiple mentions
                if text_lower.count(skill) > 1:
                    confidence += 0.1
                found_skills.append({
                    'skill': skill,
                    'confidence': min(confidence, 1.0)
                })
        
        return found_skills[:20]  # Return top 20 skills
    
    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience entries"""
        experiences = []
        
        # Find experience section
        exp_pattern = r'(?:EXPERIENCE|WORK EXPERIENCE|EMPLOYMENT)(.*?)(?:EDUCATION|PROJECTS|SKILLS|$)'
        exp_section = re.search(exp_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if exp_section:
            exp_text = exp_section.group(1)
            entries = re.split(r'\n\s*\n', exp_text)
            
            for entry in entries[:5]:  # Limit to 5 experiences
                if len(entry.strip()) < 50:
                    continue
                
                exp = {'description': entry.strip()}
                
                # Extract dates
                date_pattern = r'(\w+\s+\d{4})\s*[-–—]\s*(\w+\s+\d{4}|Present|Current)'
                dates = re.search(date_pattern, entry, re.IGNORECASE)
                if dates:
                    exp['start_date'] = dates.group(1)
                    exp['end_date'] = dates.group(2)
                
                # Extract title (often bold or first line)
                lines = entry.strip().split('\n')
                if lines:
                    exp['title'] = lines[0].strip()
                
                experiences.append(exp)
        
        return experiences
    
    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education entries"""
        education = []
        
        degree_patterns = [
            (r'Bachelor', 'Bachelor'),
            (r'Master', 'Master'),
            (r'PhD|Ph\.D', 'PhD'),
            (r'Associate', 'Associate'),
            (r'B\.?S\.?', 'Bachelor of Science'),
            (r'B\.?A\.?', 'Bachelor of Arts'),
            (r'M\.?S\.?', 'Master of Science'),
            (r'M\.?A\.?', 'Master of Arts'),
            (r'MBA', 'MBA')
        ]
        
        edu_pattern = r'(?:EDUCATION|ACADEMIC BACKGROUND)(.*?)(?:EXPERIENCE|PROJECTS|SKILLS|$)'
        edu_section = re.search(edu_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if edu_section:
            edu_text = edu_section.group(1)
            entries = re.split(r'\n\s*\n', edu_text)
            
            for entry in entries[:3]:
                edu_entry = {}
                
                for pattern, degree_name in degree_patterns:
                    if re.search(pattern, entry, re.IGNORECASE):
                        edu_entry['degree'] = degree_name
                        break
                
                if edu_entry:
                    lines = entry.strip().split('\n')
                    if lines:
                        edu_entry['institution'] = lines[0].strip()
                    
                    # Extract year
                    year_pattern = r'(19|20)\d{2}'
                    years = re.findall(year_pattern, entry)
                    if years:
                        edu_entry['year'] = years[0]
                    
                    education.append(edu_entry)
        
        return education
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        certifications = []
        
        cert_patterns = [
            r'certified', r'certification', r'aws certified', r'azure certified',
            r'pmp', r'cissp', r'cisa', r'cism', r'itil', r'scrum master'
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match not in certifications:
                    certifications.append(match)
        
        return certifications[:10]
    
    def _calculate_total_experience(self, text: str) -> float:
        """Calculate total years of experience"""
        # Look for total experience mentions
        exp_pattern = r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?experience'
        matches = re.findall(exp_pattern, text, re.IGNORECASE)
        
        if matches:
            return float(matches[0])
        
        # Alternative: parse from dates in experience section
        exp_pattern = r'(?:EXPERIENCE|WORK EXPERIENCE)(.*?)(?:EDUCATION|PROJECTS|SKILLS|$)'
        exp_section = re.search(exp_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if exp_section:
            exp_text = exp_section.group(1)
            dates = re.findall(r'(19|20)\d{2}', exp_text)
            if dates:
                return 5.0  # Default if can't calculate
        
        return 0.0
    
    def _get_highest_education(self, text: str) -> str:
        """Determine highest education level"""
        education_levels = [
            ('phd', 'PhD'),
            ('doctorate', 'PhD'),
            ('master', 'Master'),
            ('mba', 'MBA'),
            ('bachelor', 'Bachelor'),
            ('associate', 'Associate'),
            ('high school', 'High School')
        ]
        
        text_lower = text.lower()
        
        for level, display in education_levels:
            if level in text_lower:
                return display
        
        return 'Not Specified'