#!/usr/bin/python3
import simplenote
import configparser
import sys
import os

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), '..', 'simpleautonote.conf')
    if not os.path.exists(config_path):
        raise FileNotFoundError("Can't find configuration file at %s" % config_path)
    config.read(config_path)
    username = config['login']['user']
    password = config['login']['password']
    inbox_name = config['general']['inbox_name']
    if len(inbox_name) == 0:
        raise RuntimeError("Must get an inbox_name untagged_note")
    simplenote_client = simplenote.Simplenote(username, password)
    note_list, status = simplenote_client.get_note_list()
    if status != 0:
        raise RuntimeError("Failed to call get_note_list")
    num_notes_with_tags = 0
    num_notes_without_tags = 0
    notes_without_tags = []

    for note in note_list:
        if len(note['tags']) == 0 and note.get('deleted', 0) != 1:
            num_notes_without_tags += 1
            notes_without_tags.append(note)
        else:
            num_notes_with_tags += 1

    print("Found %d notes without tags" % (num_notes_without_tags))

    num_success = 0
    for untagged_note in notes_without_tags:
        note, status = simplenote_client.get_note(untagged_note['key'])
        if status != 0:
            print("Couldn't get note %s" % untagged_note)
        else:
            print(note)
            note['tags'] = [inbox_name]
            lines = note['content'].split(' ')
            name = lines[0] if len(lines) > 0 else ''
            _, status = simplenote_client.update_note(note)
            if status != 0:
                print("Failed to update note %s" % untagged_note)
            else:
                print("Added note '%s' to tag %s" % (name, inbox_name))
                num_success += 1
    print("Successfully updated %d notes" % num_success)
    if num_success != num_notes_without_tags:
        print("%d notes were NOT updated" % (num_notes_without_tags - num_success))
        sys.exit(1)
    else:
        print("Completed successfully :)")
        sys.exit(0)

