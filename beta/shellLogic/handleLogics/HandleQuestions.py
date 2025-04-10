import json
from urllib.parse import unquote

from jinja2.utils import url_quote
from tabulate import tabulate
from bs4 import BeautifulSoup  # Import BeautifulSoup for basic HTML parsing

from beta.question_scraper.app import QuestionsAPI
from beta.shellLogic.Plugin import Plugin
from mainLogic.utils.dependency_checker import re_check_dependencies
from mainLogic.utils.glv import Global

import textwrap


def wrap_text(text, width=50):
    return '\n'.join(textwrap.wrap(text, width))


def parse_html(html_content):
    """Parse basic HTML content to plain text."""
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text(separator='\n')  # Separate elements by newline


class HandleQuestions(Plugin):

    def __init__(self):
        super().__init__()
        self.add_command("ques", "Get questions from the API", r'ques', self.ques)
        self.register_commands()

    def ques(self, args):

        import argparse
        parser = argparse.ArgumentParser(description='Get questions from the API')
        parser.add_argument('-B', '--batch', help='Batch ID', required=False)
        parser.add_argument('-S', '--subject', help='Subject ID', required=False)
        parser.add_argument('-C', '--chapter', help='Chapter ID', required=False)

        args = parser.parse_args(args)

        if args.batch:
            batch_id = args.batch
        else:
            batch_id = None

        if args.subject:
            subject_id = args.subject
        else:
            subject_id = None

        if args.chapter:
            chapter_id = args.chapter
        else:
            chapter_id = None

        state, prefs = re_check_dependencies()

        token = prefs['token']
        random_id = prefs['random_id']

        qApi = QuestionsAPI(token, random_id, force=False, verbose=False)

        # Get the questions
        subjects_dat = qApi.GET_SUBJECTS()

        p_Dat = []
        headers = ['Subject Name', 'Subject ID']

        for subject in subjects_dat['subjects']:
            p_Dat.append([subject['englishName'], subject['subjectId']])

        Global.hr()
        debugger.success(f"Exams: {subjects_dat['exams']}")
        debugger.success(f"ExamCategorie: {subjects_dat['examCategory']}")
        Global.hr()

        if not subject_id:
            print(tabulate(p_Dat, headers=headers, tablefmt='grid'))

        if subject_id and not chapter_id:
            debugger.success(f"Getting chapters for subject {subject_id}")
            chapters_dat = qApi.GET_CHAPTERS(subject_id=subject_id)

            headers = ['Chapter Name', 'Chapter ID', 'Class ID', 'Easy', 'Medium', 'Hard']

            s_dat = []
            for chapter in chapters_dat:
                s_dat.append(
                    [chapter['englishName'], chapter['chapterId'], chapter['classId'], chapter['questionCountEasy'],
                     chapter['questionCountMedium'], chapter['questionCountHard']])

            Global.hr()
            print(tabulate(s_dat, headers=headers, tablefmt='grid'))
            Global.hr()

        if chapter_id and subject_id:
            debugger.success(f"Getting questions for subject {subject_id} and chapter {chapter_id}")
            questions_dat = qApi.GET_QUESTION(subject_id=subject_id, chapters=[
                {'chapterId': chapter_id, 'classId': 'oyhh7ve8217so92jw81tefbyp'}], difficulty_level=[3],
                                              questions_count=90)

            headers = ['Question ID', 'Question Text', 'Contents', 'Options', 'Type']

            s_dat = []
            for question in questions_dat['questions']:
                question_text = wrap_text(parse_html(str(question['plainQuestionText'])), 50)
                options_text = "\n".join([wrap_text(parse_html(f"* {option['text']}"), 80) for option in question['options']])
                contents = wrap_text(parse_html(str(question['content'])), 50) if 'content' in question else ''
                s_dat.append(
                    [question['questionId'], unquote(question_text), unquote(contents), unquote(options_text), question['type']]
                )

            Global.hr()
            print(tabulate(s_dat, headers=headers, tablefmt='grid'))
            Global.hr()
