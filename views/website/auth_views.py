from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash, authenticate
from django.conf import settings
from core.models import UserModel, EmailOTPModel, RoleModel, LawModel
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from utils.otp import generate_otp, send_otp_email
from django.db import transaction
from django.utils.text import slugify
# ---------------- Authentication ----------------

def user_login(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/")
        next_url = request.GET.get("next", "")
        return render(request, "website/login.html", {"next": next_url})

    email = request.POST.get("email")
    password = request.POST.get("password")
    next_url = request.POST.get("next", "")

    user = authenticate(request, email=email, password=password)
    if user:
        login(request, user)
        messages.success(request, "Login successfully.")
        if next_url:
            return redirect(next_url)
        return redirect("/")

    pending_user = UserModel.objects.filter(email=email).first()
    if pending_user and pending_user.check_password(password) and not pending_user.is_active:
        if not pending_user.is_verified:
            messages.error(
                request,
                "Your email is not verified yet. Please enter the OTP sent to your email.",
            )
        else:
            messages.error(
                request,
                "Your account is pending admin approval. Please wait for approval.",
            )
        return redirect("/" + settings.LOGIN_URL)

    messages.error(request, "Invalid email or password.")
    return redirect("/" + settings.LOGIN_URL)


def user_register(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/")
        return render(request, "website/register.html")

    username = request.POST.get("username")
    email = request.POST.get("email")
    phone = request.POST.get('phone')
    password = request.POST.get("password")
    confirm_password = request.POST.get("confirm_password")

    if password != confirm_password:
        messages.error(request, "Passwords do not match. Please try again.")
        return redirect("register")

    if UserModel.objects.filter(email=email).exists():
        messages.error(request, "Email already registered.")
        return redirect("register")

    try:
        user = UserModel.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
            is_active=False,
            is_verified=False,
        )

        otp_code = generate_otp()
        EmailOTPModel.objects.create(user=user, code=otp_code)
        send_otp_email(email, otp_code)

        messages.info(request, "We sent you an OTP to verify your account.")
        return redirect(f"/verify_otp/?email={email}&type=register")

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("register")


def verify_otp(request):
    if request.method == "GET":
        email = request.GET.get("email")
        otp_type = request.GET.get("type")
        return render(
            request, "website/verify_otp.html", {"email": email, "type": otp_type}
        )

    email = request.POST.get("email")
    otp = (request.POST.get("otp") or request.POST.get("otp_code") or "").strip()
    otp_type = request.POST.get("type")

    try:
        user = UserModel.objects.get(email=email)
    except UserModel.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect(
            "/register/" if otp_type == "register" else "/request_reset_password/"
        )

    otp_entry = (
        EmailOTPModel.objects.filter(user=user, code=otp)
        .order_by("-created_at")
        .first()
    )

    if not otp_entry or otp_entry.is_expired():
        messages.error(request, "Invalid or expired OTP.")
        return redirect(f"/verify_otp/?email={email}&type={otp_type}")

    EmailOTPModel.objects.filter(user=user).delete()

    if otp_type == "register":
        user.is_verified = True
        user.save()
        messages.success(
            request,
            "OTP verified successfully. Your account is now pending admin approval.",
        )
        return redirect("/login/")

    elif otp_type == "reset":
        messages.success(request, "OTP verified. Please reset your password.")
        return redirect(f"/reset_password/?email={email}")

    else:
        messages.error(request, "Invalid OTP type.")
        return redirect("/login/")


def resend_otp(request):
    email = request.GET.get("email")
    otp_type = request.GET.get("type")

    if not email or not otp_type:
        messages.error(request, "Invalid request.")
        return redirect("/login/")

    try:
        user = UserModel.objects.get(email=email)
    except UserModel.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect(
            "/register/" if otp_type == "register" else "/request_reset_password/"
        )

    otp_code = generate_otp()

    EmailOTPModel.objects.filter(user=user).delete()
    EmailOTPModel.objects.create(user=user, code=otp_code)

    try:
        send_otp_email(email, otp_code)
        messages.success(request, "A new OTP has been sent to your email.")
    except Exception as e:
        print("OTP send error:", e)
        messages.error(request, "Failed to send OTP. Please try again later.")

    return redirect(f"/verify_otp/?email={email}&type={otp_type}")


def request_reset_password(request):
    if request.method == "GET":
        return render(request, "website/request_reset_password.html")

    email = request.POST.get("email")

    try:
        user = UserModel.objects.get(email=email)
    except UserModel.DoesNotExist:
        messages.error(request, "No account found with that email.")
        return redirect("/request_reset_password/")

    otp_code = generate_otp()
    EmailOTPModel.objects.create(user=user, code=otp_code)
    try:
        send_otp_email(email, otp_code)
        messages.info(request, "OTP sent to your email for password reset.")
        return redirect(f"/verify_otp/?email={email}&type=reset")
    except:
        messages.error(request, "Internal Server Error")
        return redirect("/request_reset_password/")

def reset_password(request):
    email = request.GET.get("email") or request.POST.get("email")

    if request.method == "GET":
        return render(request, "website/reset_password.html", {"email": email})

    password = request.POST.get("password")
    confirm = request.POST.get("confirm_password")

    if password != confirm:
        messages.error(request, "Passwords do not match.")
        return redirect(f"/reset_password/?email={email}")

    try:
        user = UserModel.objects.get(email=email)
    except UserModel.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("/request_reset_password/")

    user.password = make_password(password)
    user.save()

    messages.success(request, "Password reset successfully. Please login.")
    return redirect("/login/")


def subscribe(request):
    if request.method != "POST":
        return redirect("index")

    username = request.POST.get("username")
    email = request.POST.get("email")
    phone = request.POST.get("phone")
    password = request.POST.get("password")
    confirm_password = request.POST.get("confirm_password")
    law_id = request.POST.get("law_id")
    payment_proof = request.FILES.get("payment_proof")

    if password != confirm_password:
        messages.error(request, "Passwords do not match. Please try again.")
        return redirect("index")

    if UserModel.objects.filter(email=email).exists():
        messages.error(request, "Email already registered.")
        return redirect("index")

    law = LawModel.objects.filter(id=law_id).first()

    try:
        user = UserModel.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
            payment_proof=payment_proof,
            subscription_law=law,
            is_active=False,
            is_verified=False,
        )

        otp_code = generate_otp()
        EmailOTPModel.objects.create(user=user, code=otp_code)
        send_otp_email(email, otp_code)

        messages.info(
            request,
            "We sent you an OTP to verify your account after payment. Please check your email.",
        )
        return redirect(f"/verify_otp/?email={email}&type=register")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect("index")


def user_logout(request):
    logout(request)
    return redirect("/" + settings.LOGIN_URL)


# ---------------- Profile Management ----------------
@login_required(login_url="/" + settings.LOGIN_URL)
def update_profile(request):
    user = request.user
    if request.method == "POST":
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.phone = request.POST.get("phone")
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")
    return render(request, "website/profile.html")

@login_required(login_url="/" + settings.LOGIN_URL)
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")

        user = request.user

        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("profile")

        if current_password == new_password:
            messages.error(request, "New password cannot be same as current password.")
            return redirect("profile")

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)

        messages.success(request, "Your password has been updated successfully.")
        return redirect("profile")