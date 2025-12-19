from profiles.models import FreelancerProfile

def get_freelancer_profiles_map(freelancer_ids):
    profiles = (
        FreelancerProfile.objects
        .select_related("user")
        .filter(id__in=freelancer_ids)
    )

    return {
        p.id: {
            "profile_id": p.id,
            "user_id": p.user_id,
            "full_name": p.full_name,
            "email": p.user.email if p.user else None,
            "profile_image": p.profile_image.url if p.profile_image else None,
        }
        for p in profiles
    }
