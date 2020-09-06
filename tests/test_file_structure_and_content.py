"""Tests the file structure and contents of downloaded files."""

import filecmp
from datetime import date
from pathlib import Path

from sec_edgar_downloader._constants import (
    DATE_FORMAT_TOKENS,
    FILING_DETAILS_FILENAME_STEM,
    FILING_FULL_SUBMISSION_FILENAME,
)


def test_file_structure(downloader):
    """
    Ensure that the file directory looks as follows,
    with 4 directories and 2 files:

    └── sec_edgar_filings
        └── AAPL
            ├── 10-K
            │   └── 0000320193-19-000119.txt
            └── 8-K
                └── 0001193125-19-292676.txt
    """
    dl, dl_path = downloader

    assert len(list(dl_path.glob("*"))) == 0

    filing_type = "8-K"
    ticker = "AAPL"

    # get the latest 8-K for AAPL
    num_downloaded = dl.get(filing_type, ticker, 1, download_details=False)
    assert num_downloaded == 1

    filings_save_path = dl_path / "sec_edgar_filings"
    assert filings_save_path.exists()
    assert filings_save_path.is_dir()
    assert len(list(filings_save_path.glob("*"))) == 1

    ticker_save_path = filings_save_path / ticker
    assert ticker_save_path.exists()
    assert ticker_save_path.is_dir()
    assert len(list(ticker_save_path.glob("*"))) == 1

    filing_type_save_path = ticker_save_path / filing_type
    assert filing_type_save_path.exists()
    assert filing_type_save_path.is_dir()

    downloaded_filings = list(filing_type_save_path.glob("*"))
    assert len(downloaded_filings) == 1
    assert downloaded_filings[0].is_file()

    # get the latest 10-K for AAPL, including the detail HTML file
    filing_type = "10-K"
    num_downloaded = dl.get(filing_type, ticker, 1, download_details=True)
    assert num_downloaded == 1

    # ensure that the 10-K was added to the existing AAPL dir
    assert len(list(ticker_save_path.glob("*"))) == 2

    filing_type_save_path = ticker_save_path / filing_type
    assert filing_type_save_path.exists()
    assert filing_type_save_path.is_dir()

    downloaded_filings = list(filing_type_save_path.glob("*"))
    assert len(downloaded_filings) == 2
    assert downloaded_filings[0].is_file()
    assert downloaded_filings[1].is_file()
    assert len(list(filing_type_save_path.glob(FILING_FULL_SUBMISSION_FILENAME))) == 1
    assert (
        len(list(filing_type_save_path.glob(f"{FILING_DETAILS_FILENAME_STEM}.html")))
        == 1
    )


# TODO: test file contents of detail file (e.g. xml)
def test_file_contents(downloader):
    dl, dl_path = downloader

    filing_type = "8-K"
    ticker = "AAPL"
    before_date = date(2019, 11, 15).strftime(DATE_FORMAT_TOKENS)

    num_downloaded = dl.get(
        filing_type, ticker, 1, before=before_date, download_details=False
    )
    assert num_downloaded == 1

    downloaded_file_path = dl_path / "sec_edgar_filings" / ticker / filing_type
    downloaded_filings = list(downloaded_file_path.glob("*"))
    assert len(downloaded_filings) == 1
    downloaded_file_path = downloaded_file_path / downloaded_filings[0]

    # https://stackoverflow.com/q/1072569
    expected_data_path = Path(f"tests/sample_filings/apple_8k_{before_date}.txt")
    if expected_data_path.exists():
        # Only run this check if the sample filing exists
        # This check is required since the distributed python package will not
        # contain the sample filings test data due to size constraints
        assert filecmp.cmp(expected_data_path, downloaded_file_path, shallow=False)
