import argparse
from beta.obsolete.batch_scraper.app import BatchAPI
from beta.shellLogic.Plugin import Plugin
from mainLogic.utils.dependency_checker import re_check_dependencies
from mainLogic.utils.glv_var import debugger


class HandleBatch(Plugin):
    def __init__(self):
        super().__init__()
        self.add_command("bgen", "Generate entire batch data", "--generate", self.generate)
        self.register_commands()

    def generate(self, args):
        parser = argparse.ArgumentParser(description="Generate batch data")
        parser.add_argument("--khazana", "-K", type=str, default="")
        parser.add_argument("--batch-slug", "-B", type=str, default="")
        parser.add_argument("--subject-slug", "-S", type=str, default="")
        parser.add_argument("--chapter-slug", "-C", type=str, default="")
        parser.add_argument("--export", "-E", type=str, default="")
        parser.add_argument("--simple", action="store_true", default=False)
        parser.add_argument("--recursive", action="store_true", default=False)

        opts = parser.parse_args(args)

        state, prefs = re_check_dependencies(reload=True)
        token = prefs['token']


        def to_csv_str(data: list):
            headers = data[0].keys()
            rows = [list(item.values()) for item in data]
            output = []
            output.append(','.join(headers))
            for row in rows:
                output.append(','.join(map(str, row)))
            return '\n'.join(output)


        def get_khazana_data(khazana_name):
            api = BatchAPI(khazana_name, token, force=False, verbose=False)
            res = api.GET_KHAZANA_SUBJECTS()
            if not res:
                debugger.error(f"Batch {khazana_name} not found.")
                return
            else:
                debugger.info(f"Batch {khazana_name} found.")
                debugger.info(f"Batch data:\n{to_csv_str(res)}")
                return res





        # TO NOTE
        # In khazana flow, we use GET_KHAZANA_BATCHES when we actually want to get SUBJECTS
        # PREVIOUSLY we called them BATCHES as each khazana is a super class of subjects with batches inside of each subject





        # SUPER SUBJECT is a collection of teachers teaching the smae subject in different batches
        # data inside super subject
        def KHAZANA_GET_SUPER_SUBJECT_DATA(khazana_name, super_subject_name):
            api = BatchAPI(khazana_name, token, force=False, verbose=False)

            res = api.GET_KHAZANA_BATCHES(super_subject_name)

            # if super subject doe snot exixst
            if not res:
                debugger.error(f"Super subject {super_subject_name} not found.")
                return
            else:
                debugger.info(f"Super subject {super_subject_name} found.")
                debugger.success(f"Super subject data:\n{to_csv_str(res)}")
                return res

        def KHAZANA_SUPER_SUBJECT_BATCH_DATA(khazana_name, super_subject_name, batch_name):
            api = BatchAPI(khazana_name, token, force=False, verbose=False)



            res = api.GET_KHAZANA_CHAPTERS(batch_name)

            # if batch does not exist
            if not res:
                debugger.error(f"Batch {batch_name} not found.")
                return
            else:
                debugger.info(f"Batch {batch_name} found.")
                debugger.success(f"Batch data:\n{to_csv_str(res)}")
                return res

        def KHAZANA_BATCH_CHAPTER_DATA(khazana_name, super_subject_name, batch_name, chapter_name):
            api = BatchAPI(khazana_name, token, force=False, verbose=False)

            res = api.GET_KHAZANA_LECTURES(batch_name, chapter_name, chapter_name)

            # if chapter does not exist
            if not res:
                debugger.error(f"Chapter {chapter_name} not found.")
                return
            else:
                debugger.info(f"Chapter {chapter_name} found.")
                debugger.success(f"Chapter data:\n{to_csv_str(res)}")
                return res

        # khazana flow
        """
        #   khazana[batch] ---> super-subject[batch] ---> batch ---> chapter ---> lectures 
        """

        if opts.khazana:
            api = BatchAPI(opts.khazana, token, force=False, verbose=False)


            if opts.khazana and opts.batch_slug and opts.subject_slug and opts.chapter_slug:
                # khazana[batch] ---> super-subject[batch] ---> batch ---> chapter ---> lectures
                debugger.info(f"Generating data for khazana: {opts.khazana}, super_subject: {opts.batch_slug}, batch: {opts.subject_slug}, chapter: {opts.chapter_slug}")
                chapter = KHAZANA_BATCH_CHAPTER_DATA(opts.khazana, opts.batch_slug, opts.subject_slug, opts.chapter_slug)

                if not chapter:
                    debugger.error(f"Chapter {opts.chapter_slug} not found.")
                    return
                else:
                    debugger.info(f"Chapter data:\n{to_csv_str(chapter)}")
                    return chapter

            if opts.batch_slug and opts.subject_slug:
                batch = KHAZANA_SUPER_SUBJECT_BATCH_DATA(opts.khazana, opts.batch_slug, opts.subject_slug)

                if not batch:
                    debugger.error(f"Batch {opts.subject_slug} not found.")
                    return
                else:
                    debugger.info(f"Batch data:\n{to_csv_str(batch)}")
                    return batch


            if opts.batch_slug:
                # Batch slug is actually used here for super subject
                # khazana[batch] ---> super-subject[batch]

                debugger.info(f"Generating data for super_subject: {opts.batch_slug}")
                super_subject = KHAZANA_GET_SUPER_SUBJECT_DATA(opts.khazana, opts.batch_slug)

                if not super_subject:
                    debugger.error(f"Super subject {opts.batch_slug} not found.")
                    return
                else:
                    debugger.info(f"Super subject data:\n{to_csv_str(super_subject)}")
                    return super_subject










            debugger.info(f"Generating super-subjects for khazana batch: {opts.khazana}")
            super_subjects = api.GET_KHAZANA_SUBJECTS()
            debugger.info(f"Got this data for super-subjects for khazana batch: {opts.khazana}")
            debugger.success(f"{to_csv_str(super_subjects)}")




        else:
            # normal flow
            api = BatchAPI(opts.batch_slug, token, force=False, verbose=False)



