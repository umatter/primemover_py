import src


if __name__ == "__main__":
    src.worker.api_wrapper.fetch_results()
    src.Results.process_results(set_reviewed=False)
