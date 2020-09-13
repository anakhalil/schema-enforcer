from typing import List, Optional, Any
from pydantic import BaseModel, validator
from termcolor import colored

RESULT_PASS = "PASS"
RESULT_FAIL = "FAIL"


class ValidationResult(BaseModel):
    """The ValidationResult object is meant to store the result of a given test 
    along with some contextual information about the test itself.
    """

    result: str
    schema_id: str
    instance_name: Optional[str]
    instance_location: Optional[str]
    instance_type: Optional[str]
    source: Any = None
    strict: bool = False

    # if failed
    absolute_path: Optional[List[str]] = []
    message: Optional[str]

    @validator("result")
    def result_must_be_pass_or_fail(cls, v):
        if v.upper() not in [RESULT_PASS, RESULT_FAIL]:
            raise ValueError("must be either PASS or FAIL")
        return v.upper()

    def passed(self):
        """Return True or False to indicate if the test has passed.
        
        Returns
            Bool: indicate if the test passed or failed
        """
        if self.result == RESULT_PASS:
            return True

        return False

    def print(self):
        """Print the result of the test in CLI."""
        if self.passed():
            self.print_passed()
        else:
            self.print_failed()

    def print_failed(self):
        """Print the result of the test to CLI when the test failed."""
        print(
            colored(f"FAIL", "red") + f" | [ERROR] {self.message}"
            f" [{self.instance_type}] {self.instance_location}/{self.instance_name}"
            f" [PROPERTY] {':'.join(str(item) for item in self.absolute_path)}"
        )

    def print_passed(self):
        """Print the result of the test to CLI when the test passed."""
        print(colored(f"PASS", "green") + f" [{self.instance_type}] {self.instance_location}/{self.instance_name}")
