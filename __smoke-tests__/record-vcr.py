from hotglue_smoke_test.vcr.tap import VCRTapTestRunner

from tap_rillet.tap import TapRillet


class Runner(VCRTapTestRunner):
    PRESERVE_KEYS = {"next_cursor"}

    def module(self) -> str:
        return "tap_rillet.tap"

    def launch(self):
        TapRillet.cli()


if __name__ == "__main__":
    Runner.main()
