import os

from utilities.collab import can_access, create_project, add_collaborator, can_share, share_privilege, unshare_privilege
from utilities.user import create_user, get_user
from utilities.resource import create_resource


def main():

    """
    Here I will update the progress:

        (1) create_project(): Takes a project id and registers the project in the system
        (2) add_collaborator(): Adds set of collaborators to an existing project
        (3) can_share(): Takes from and to user ids and resource local path, and the project id to authorize the sharing
        (4) share():
    """

    create_project(project_id="P2")

    add_collaborator(project_id="P2", users={"pwn_dp", "Bailey", "Cathy"})

    can_share(from_username="pwn_dp", resource_id="data.json", to_username="Bailey", project_id="P2")
    can_share(from_username="pwn_dp", resource_id="data2.json", to_username="Cathy", project_id="P2")
    can_share(from_username="Bailey", resource_id="data2.json", to_username="Cathy", project_id="P2")
    can_share(from_username="pwn_dp", resource_id="data2.json", to_username="sefcom", project_id="P2")



    # t = 2: Alex invites collaborator Bailey and Cathy
    # invite_collaborator(user_id=creator, project_id="P1", users={"Bailey"})
    # invite_collaborator(user_id=creator, project_id="P1", users={"Cathy"})

    # t = 3: Alex shares resource Alex_1 with Bailey and Cathy
    # share_privilege(project_id="P1", from_user_id=creator, resource_id_to_share="/home/pwn_dp/papers.txt",
    #                 to_user_ids={"Bailey"})
    # share_privilege(project_id="P1", from_user_id=creator, resource_id_to_share="/home/pwn_dp/papers.txt",
    #                 to_user_ids={"Cathy"})

    # t = 4: Alex shares resources Alex_2 Alex_3 with Bailey and Cathy
    # share_privilege(project_id="P1", from_user_id=creator, resource_id_to_share="/home/pwn_dp/references.txt",
    #                 to_user_ids={"Bailey", "Cathy"})
    # share_privilege(project_id="P1", from_user_id=creator, resource_id_to_share="/home/pwn_dp/data.json",
    #                 to_user_ids={"Bailey", "Cathy"})

    # t = 5: Alex shares Alex_4 only with Bailey
    # share_privilege(project_id="P1", from_user_id=creator, resource_id_to_share="/home/pwn_dp/data2.json",
    #                 to_user_ids={"Bailey"})
    #
    # # t = 6: Bailey shares Bailey_1 only with Cathy
    # share_privilege(project_id="P1", from_user_id="Bailey", resource_id_to_share="/home/pwn_dp/bailey_results.json",
    #                 to_user_ids={"Cathy"})

    # t = 7: Alex invites collaborator Drew
    # invite_collaborator(user_id=creator, project_id="P1", users={"Drew"})

    # t = 8: Alex shares Alex_3 with Drew (Example of Privilege Elevation)
    # share_privilege(project_id="P1", from_user_id=creator, resource_id_to_share="/home/pwn_dp/data.json",
    #                 to_user_ids={"Drew"})

    # t = 9: Bailey shares Bailey_1 with Drew (Example of Privilege Elevation)
    # share_privilege(project_id="P1", from_user_id="Bailey", resource_id_to_share="/home/pwn_dp/bailey_results.json",
    #                 to_user_ids={"Drew"})

    # t = 10: Alex un-shares Alex_3 with Drew (Example of Privilege Descent)
    # unshare_privilege(project_id="P1", from_user_id=creator, resource_id_to_unshare="/home/pwn_dp/data.json",
    #                   to_user_ids={"Drew"})

    # t = 11: Alex removes Drew from the project


if __name__ == "__main__":
    main()
