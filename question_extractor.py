import re
import logging
from typing import List, Optional
from models import QuestionData

logger = logging.getLogger(__name__)

class QuestionExtractor:
    """Extract MCQ questions from parsed PDF text"""
    
    @staticmethod
    def extract_questions(text: str) -> List[QuestionData]:
        """
        Parse text and extract questions, options, and answers
        
        Args:
            text: Full text extracted from PDF
            
        Returns:
            List of QuestionData objects
        """
        questions = []
        
        # Split text into question blocks using numbered pattern
        # Pattern: 1. or 2. or 10. etc at start of line
        # We look for a digit followed by a dot, at the start of a line
        question_pattern = r'(?=^\d+\.)'
        blocks = re.split(question_pattern, text, flags=re.MULTILINE)
        
        # Remove empty blocks
        blocks = [b.strip() for b in blocks if b.strip()]
        
        for block in blocks:
            try:
                question_data = QuestionExtractor._parse_question_block(block)
                if question_data:
                    questions.append(question_data)
            except Exception as e:
                logger.warning(f"Failed to parse question block: {str(e)}")
                continue
        
        logger.info(f"Extracted {len(questions)} questions")
        return questions
    
    @staticmethod
    def _parse_question_block(block: str) -> Optional[QuestionData]:
        """
        Parse a single question block
        
        Expected format example:
        1. What is the capital of France?
        a) London
        b) Berlin
        # Paris
        d) Madrid
        """
        lines = block.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        if not lines:
            return None
        
        # 1. Extract Question
        # Matches "1. Text" or "1) Text"
        question_match = re.match(r'^\d+[\.\)]\s*(.+)$', lines[0])
        if not question_match:
            return None
            
        question_text = question_match.group(1).strip()
        
        options = []
        correct_answer = None
        
        # Helper to extract text from "a) Text" or "a. Text"
        def extract_option_text(text):
            # match "a) " or "a. "
            m = re.match(r'^[a-zA-Z][\.\)]\s*(.+)$', text)
            return m.group(1).strip() if m else text

        # 2. Extract Options
        for line in lines[1:]:
            line = line.strip()
            
            # Check for Correct Answer starting with #
            if line.startswith('#'):
                # Found correct answer
                # Remove '#'
                raw_content = line[1:].strip()
                # If it looks like "# c) Paris", extract "Paris"
                # If it looks like "# Paris", extract "Paris"
                opt_text = extract_option_text(raw_content)
                
                options.append(opt_text)
                correct_answer = opt_text
            
            # Check for standard option start "a) ..." or "A. ..."
            elif re.match(r'^[a-zA-Z][\.\)]\s+', line):
                opt_text = extract_option_text(line)
                options.append(opt_text)
            
            else:
                # Continuation line
                # If we have options, append to last option
                if options:
                    options[-1] += " " + line
                else:
                    # Append to question text
                    question_text += " " + line
                    
        # Validate we found options and a correct answer
        if len(options) < 2:
            return None
            
        if not correct_answer:
            return None
            
        return QuestionData(
            question=question_text,
            options=options,
            answer=correct_answer
        )
