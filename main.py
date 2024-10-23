import uuid
import argparse
import questionary
import tzlocal
from datetime import datetime
from colorama import init, Style

from common.logger import log_message
from common.agent import handle_user_prompt, setup_services
from common.chat import get_conversation_label


init(autoreset=True)

# menu prompts
continue_conversation = "Continue a previous conversation"
ask_new_question = "Ask a new question"
troubleshoot_problem = "Troubleshoot a problem"
select_profile = "Select a different profile"
configure_profile = "Configure the profile"
exit_item = "Exit"


def text_based_interaction(profile: str):
    while True:
        choice = questionary.select(
            "Choose an option:",
            use_shortcuts=True,
            choices=[
                continue_conversation,
                ask_new_question,
                troubleshoot_problem,
                select_profile,
                configure_profile,
                exit_item,
            ],
        ).ask()  # Returns the selected choice as a string

        if choice == configure_profile:
            log_message("INFO", "Configuring the profile...")
            profile_name = questionary.text("Enter the new profile name:").ask()
            log_message("INFO", f"New profile name: {profile_name}")

        elif choice == ask_new_question or choice == troubleshoot_problem:
            troubleshooting = False
            if choice == troubleshoot_problem:
                troubleshooting = True

            setup_services(profile)
            first_question = True
            conversation_details = {}

            while True:
                if first_question:
                    if troubleshooting:
                        prompt = "Describe the problem you are experiencing: "
                    else:
                        prompt = "Enter your question: "
                else:
                    prompt = "Enter your follow-up question: "

                question = questionary.text(prompt, multiline=False).ask()
                if question is None or question == "":
                    print("Returning to the main menu...")
                    break

                if first_question:
                    first_question = False
                    conversation_name = get_conversation_label(profile, question)
                    session_id = str(uuid.uuid4())
                    conversation_details = {
                        "start_time": datetime.now(),
                        "session_id": session_id,
                        "conversation_name": conversation_name,
                        "conversation_type": "troubleshooting"
                        if troubleshooting
                        else "question",
                        "conversation_history": [],
                    }

                if troubleshooting:
                    local_tz = tzlocal.get_localzone()
                    current_time = datetime.now(local_tz)
                    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

                    question_full = (
                        "Using available tools, investigate the alert/issue provided below in XML tag "
                        "<issue_to_investigate>. "
                        "Review all reasonable scenarios "
                        "why the problem could happen. Use available tooling to collect "
                        "necessary debugging information. Perform Root Cause Analysis. "
                        "Suggest remediation steps. "
                        "Using bullet points, mention a summary of taken investigation steps. "
                        f"The current GMT date/time is {formatted_time}.\n\n"
                        f"<issue_to_investigate>{question}</issue_to_investigate>"
                    )

                answer = handle_user_prompt(
                    profile,
                    question if not troubleshooting else question_full,
                    conversation_details["conversation_history"],
                )

                print(Style.BRIGHT + "Answer: " + Style.RESET_ALL + answer)
                conversation_details["conversation_history"].append(
                    {"question": question, "answer": answer}
                )
                log_message("INFO", f"Conversation details: {conversation_details}")

        else:
            print("Exiting...")
            break


def main():
    parser = argparse.ArgumentParser(description="CLI Application Options")
    parser.add_argument(
        "--mode",
        "-m",
        type=str,
        help="Select mode: interactive (default) or command",
        choices=["interactive", "command"],
    )
    parser.add_argument(
        "--profile",
        "-p",
        type=str,
        help='Configuration profile to use (the default is "default")',
    )

    args = parser.parse_args()
    profile = "default"

    if args.profile:
        log_message("INFO", f"Using profile: {args.profile}")
        profile = args.profile
    log_message("INFO", f"Using profile: {profile}")

    mode = "interactive"
    if args.mode == "interactive":
        mode = "interactive"

    log_message("INFO", f"Running in {mode} mode")
    text_based_interaction(profile)


if __name__ == "__main__":
    main()
