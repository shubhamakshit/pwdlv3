import argparse
from tabulate import tabulate

from beta.batch_scraper.app import BatchAPI
from beta.shellLogic.Plugin import Plugin
from mainLogic.utils.dependency_checker import re_check_dependencies


class HandleBatch(Plugin):

    def __init__(self):
        super().__init__()
        self.add_command("bgen", "Generate entire batch data", "--generate", self.generate)
        self.register_commands()

    def generate(self, args):
        # Set up the argument parser
        parser = argparse.ArgumentParser(description="Generate batch data.")
        parser.add_argument("--khazana", "-K", type=str, help="Khazana slug", default="")
        parser.add_argument('--batch-slug', '-B', type=str, help='Batch slug to use',default='')
        parser.add_argument('--subject-slug', '-S', type=str, help='Level of recursion', default="")
        parser.add_argument("--chapter-slug", "-C", type=str, help="Chapter slug", default="")

        # Parse the arguments
        parsed_args = parser.parse_args(args)

        khazana = parsed_args.khazana
        batch_slug = parsed_args.batch_slug
        subject_slug = parsed_args.subject_slug
        chapter_slug = parsed_args.chapter_slug

        # Get the batch data
        state, prefs = re_check_dependencies(reload=True)

        token = prefs['token']
        api = BatchAPI(batch_slug if not khazana else khazana, token, False)

        if khazana:
            subjects_k = api.GET_KHAZANA_SUBJECTS()
            headers, data = BatchAPI.to_table(subjects_k)
            print(tabulate(data, headers=headers, tablefmt="pretty"))

            if batch_slug:
                batch_data = api.GET_KHAZANA_BATCHES(batch_slug)
                headers, data = BatchAPI.to_table(batch_data)
                print(tabulate(data, headers=headers, tablefmt="pretty"))

            if batch_slug and subject_slug:
                chapter_data = api.GET_KHAZANA_CHAPTERS(subject_slug)
                headers, data = BatchAPI.to_table(chapter_data)
                print(tabulate(data, headers=headers, tablefmt="pretty"))

            if batch_slug and subject_slug and chapter_slug:
                topic_data = api.GET_KHAZANA_LECTURES(batch_slug, subject_slug, chapter_slug)
                headers, data = BatchAPI.to_table(topic_data)
                print(tabulate(data, headers=headers, tablefmt="pretty"))


        batch_data = api.GET_NORMAL_SUBJECTS()

        headers, data = BatchAPI.to_table(batch_data)
        print(tabulate(data, headers=headers, tablefmt="pretty"))

        if subject_slug:
            chapter_data = api.GET_NORMAL_CHAPTERS(subject_slug)

            headers, data = BatchAPI.to_table(chapter_data)

            print(tabulate(data, headers=headers, tablefmt="pretty"))

        if subject_slug and chapter_slug:
            topic_data = api.GET_NORMAL_LECTURES(subject_slug, chapter_slug)

            headers, data = BatchAPI.to_table(topic_data)

            print(tabulate(data, headers=headers, tablefmt="pretty"))


