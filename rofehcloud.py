import uuid
import argparse
import questionary
import tzlocal
from datetime import datetime
from colorama import init, Style

from common.logger import log_message
from common.agent import handle_user_prompt, setup_services
from common.chat import (
    get_conversation_label,
    save_data,
    load_data,
    get_conversations_list,
)
from common.config import Config as config
from common.profile import get_profiles
from common.utils import initialize_environment


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
            "Choose an option (or use Ctrl+C to exit):",
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
            log_message("DEBUG", "Configuring the profile...")
            profile_name = questionary.text("Enter the new profile name:").ask()
            log_message("DEBUG", f"New profile name: {profile_name}")

        elif choice == select_profile:
            profiles = get_profiles()
            if not profiles:
                print("No profiles found.")
                continue

            formatted_profiles = []
            for profile in profiles:
                formatted_profiles.append(f"{profile['name']} ({profile['description']})")

            profile_name = questionary.select(
                "Select a profile (press Ctrl+C to exit the menu):",
                use_shortcuts=True,
                choices=formatted_profiles,
            ).ask()

            if profile_name is None:
                print("Returning to the main menu...")
                continue
            
            profile = profile_name

        elif (
            choice == continue_conversation
            or choice == ask_new_question
            or choice == troubleshoot_problem
        ):
            troubleshooting = False
            if choice == troubleshoot_problem:
                troubleshooting = True

            setup_services(profile)
            first_question = True
            conversation_details = {}
            session_id = None

            if choice == continue_conversation:
                conversations_list = get_conversations_list(profile)
                if not conversations_list:
                    print("No conversations found.")
                    continue
                formatted_conversations_list = []
                for conversation in conversations_list:
                    formatted_conversations_list.append(
                        f"{conversation['label']} (started on {conversation['date']}, "
                        f"session ID {conversation['session_id']})"
                    )

                conversation_to_continue = questionary.select(
                    "Select a conversation to continue (press Ctrl+C to exit the menu):",
                    use_shortcuts=True,
                    choices=formatted_conversations_list,
                ).ask()

                if conversation_to_continue is None:
                    print("Returning to the main menu...")
                    continue

                session_id = conversation_to_continue.split("session ID ")[1].strip(")")
                log_message("DEBUG", f"Session ID: {session_id}")

                session_file_name = f"{config.SESSION_DIR}/{session_id}.yaml"
                conversation_details = load_data(session_file_name)
                if not conversation_details:
                    print("Error while loading the conversation details.")
                    continue
                print(
                        Style.BRIGHT
                        + "\nConversation history: \n"
                    )
                for chat_entry in conversation_details["conversation_history"]:
                    print(
                        Style.BRIGHT
                        + "Question: "
                        + Style.RESET_ALL
                        + chat_entry["question"]
                    )
                    print(
                        Style.BRIGHT
                        + "Answer: "
                        + Style.RESET_ALL
                        + chat_entry["answer"]
                    )

                first_question = False

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
                    conversation_label = get_conversation_label(profile, question)
                    session_id = str(uuid.uuid4())
                    conversation_details = {
                        "start_time": datetime.now(),
                        "profile": profile,
                        "session_id": session_id,
                        "conversation_label": conversation_label,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "conversation_type": "troubleshooting"
                        if troubleshooting
                        else "question",
                        "conversation_history": [],
                    }

                session_file_name = f"{config.SESSION_DIR}/{session_id}.yaml"

                if troubleshooting and troubleshooting:
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

                result = save_data(session_file_name, conversation_details)
                if not result:
                    print(
                        f"Error while saving the conversation details to file {session_file_name}."
                    )
                    break

                log_message("DEBUG", f"Conversation details: {conversation_details}")

        else:
            print("Exiting...")
            break


def main():
    result = initialize_environment()
    if not result:
        exit(1)

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
        log_message("DEBUG", f"Using profile: {args.profile}")
        profile = args.profile
    print(Style.BRIGHT + "Profile: " + Style.RESET_ALL + profile)

    mode = "interactive"
    if args.mode == "interactive":
        mode = "interactive"

    log_message("DEBUG", f"Running in {mode} mode")
    text_based_interaction(profile)


if __name__ == "__main__":
    main()
