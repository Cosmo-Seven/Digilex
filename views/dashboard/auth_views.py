from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password
from core.models import UserModel
from utils.decorators import custom_login_required


# ========================
# Dashboard Login
# ========================
def dashboard_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = UserModel.objects.get(email=email)
            if check_password(password, user.password):
                login(request, user)
                messages.success(request, f"Welcome {user.username}")
                return redirect("dashboard")
            else:
                messages.error(request, "Email or Password is incorrect!")
                return redirect("dashboard_login")
        except UserModel.DoesNotExist:
            messages.error(request, "Email or Password is incorrect!")
            return redirect("dashboard_login")

    return render(request, "dashboard/login.html")


# ========================
# Dashboard Logout
# ========================
def dashboard_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("dashboard_login")


# ========================
# User Profile
# ========================
@custom_login_required("dashboard_login")
def profile(request):
    try:
        user = get_object_or_404(UserModel, id=request.user.id)

        if request.method == "POST":
            username = request.POST.get("username")
            phone = request.POST.get("phone")
            current_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            profile_file = request.FILES.get("profile")

            user.username = username
            user.phone = phone

            # Update profile picture
            if profile_file:
                if user.profile:
                    user.profile.delete(save=False)
                user.profile = profile_file

            # Update password
            if current_password or new_password or confirm_password:
                if not check_password(current_password, user.password):
                    messages.error(request, "Current password is incorrect.")
                    return redirect("profile")

                if current_password == new_password:
                    messages.warning(
                        request, "New password should not be same as old password."
                    )
                    return redirect("profile")

                if new_password != confirm_password:
                    messages.error(
                        request, "New password and confirm password do not match."
                    )
                    return redirect("profile")

                if len(new_password) < 6:
                    messages.error(
                        request, "New password must be at least 6 characters long."
                    )
                    return redirect("profile")

                user.set_password(new_password)
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully!")

            user.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")

        # GET request
        context = {"user": user}
        return render(request, "dashboard/profile.html", context)

    except Exception as e:
        messages.error(request, f"Error : {str(e)}")
        return redirect("dashboard")
