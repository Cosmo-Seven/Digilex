/**
 * RetinaLogo
 * Contact Form
 * Header Fixed
 * alert box
 */

(function ($) {
  "use strict";

  var themesflatTheme = {
    // Main init function
    init: function () {
      this.config();
      this.events();
    },

    // Define vars for caching
    config: function () {
      this.config = {
        $window: $(window),
        $document: $(document),
      };
    },

    // Events
    events: function () {
      var self = this;

      // Run on document ready
      self.config.$document.on("ready", function () {
        // Retina Logos
        self.retinaLogo();
      });

      // Run on Window Load
      self.config.$window.on("load", function () {});
    },
  }; // end themesflatTheme

  // Start things up
  themesflatTheme.init();

  /* RetinaLogo
  ------------------------------------------------------------------------------------- */
  var retinaLogos = function () {
    var retina = window.devicePixelRatio > 1 ? true : false;
    if (retina) {
      $("#site-logo-inner").find("img").attr({
        src: "static/website/images/logo.png",
        width: "197",
        height: "48",
      });

      $("#logo-footer.style").find("img").attr({
        src: "static/website/images/logo-footer.png",
        width: "197",
        height: "48",
      });
      $("#logo-footer.style2").find("img").attr({
        src: "static/website/images/logo.png",
        width: "197",
        height: "48",
      });
    }
  };

  /* Header Fixed
  ------------------------------------------------------------------------------------- */
  var headerFixed = function () {
    if ($("header").hasClass("header-fixed")) {
      var nav = $("#header");
      if (nav.length) {
        var offsetTop = nav.offset().top,
          headerHeight = nav.height(),
          injectSpace = $("<div>", {
            height: headerHeight,
          });
        injectSpace.hide();

        $(window).on("load scroll", function () {
          if ($(window).scrollTop() > 0) {
            nav.addClass("is-fixed");
            injectSpace.show();
            $("#trans-logo").attr("src", "images/logo/logo.png");
          } else {
            nav.removeClass("is-fixed");
            injectSpace.hide();
            $("#trans-logo").attr("src", "images/logo/logo-white.png");
          }
        });
      }
    }
  };

  $("#showlogo").prepend(
    '<a href="index.html"><img id="theImg" src="static/website/images/logo2.png" /></a>',
  );

  // =========NICE SELECT=========
  $(".select_js").niceSelect();

  new WOW().init();

  //Submenu Dropdown Toggle
  if ($(".main-header li.dropdown2 ul").length) {
    $(".main-header li.dropdown2").append('<div class="dropdown2-btn"></div>');

    //Dropdown Button
    $(".main-header li.dropdown2 .dropdown2-btn").on("click", function () {
      $(this).prev("ul").slideToggle(500);
    });

    //Disable dropdown parent link
    $(".navigation li.dropdown2 > a").on("click", function (e) {
      e.preventDefault();
    });

    //Disable dropdown parent link
    $(
      ".main-header .navigation li.dropdown2 > a,.hidden-bar .side-menu li.dropdown2 > a",
    ).on("click", function (e) {
      e.preventDefault();
    });

    $(".price-block .features .arrow").on("click", function (e) {
      $(e.target.offsetParent.offsetParent.offsetParent).toggleClass(
        "active-show-hidden",
      );
    });
  }

  // Mobile Nav Hide Show
  if ($(".mobile-menu").length) {
    //$('.mobile-menu .menu-box').mCustomScrollbar();

    var mobileMenuContent = $(".main-header .nav-outer .main-menu").html();
    $(".mobile-menu .menu-box .menu-outer").append(mobileMenuContent);
    $(".sticky-header .main-menu").append(mobileMenuContent);

    //Hide / Show Submenu
    $(".mobile-menu .navigation > li.dropdown2 > .dropdown2-btn").on(
      "click",
      function (e) {
        e.preventDefault();
        var target = $(this).parent("li").children("ul");
        var args = { duration: 300 };
        if ($(target).is(":visible")) {
          $(this).parent("li").removeClass("open");
          $(target).slideUp(args);
          $(this)
            .parents(".navigation")
            .children("li.dropdown2")
            .removeClass("open");
          $(this)
            .parents(".navigation")
            .children("li.dropdown2 > ul")
            .slideUp(args);
          return false;
        } else {
          $(this)
            .parents(".navigation")
            .children("li.dropdown2")
            .removeClass("open");
          $(this)
            .parents(".navigation")
            .children("li.dropdown2")
            .children("ul")
            .slideUp(args);
          $(this).parent("li").toggleClass("open");
          $(this).parent("li").children("ul").slideToggle(args);
        }
      },
    );

    //3rd Level Nav
    $(
      ".mobile-menu .navigation > li.dropdown2 > ul  > li.dropdown2 > .dropdown2-btn",
    ).on("click", function (e) {
      e.preventDefault();
      var targetInner = $(this).parent("li").children("ul");

      if ($(targetInner).is(":visible")) {
        $(this).parent("li").removeClass("open");
        $(targetInner).slideUp(500);
        $(this)
          .parents(".navigation > ul")
          .find("li.dropdown2")
          .removeClass("open");
        $(this)
          .parents(".navigation > ul")
          .find("li.dropdown > ul")
          .slideUp(500);
        return false;
      } else {
        $(this)
          .parents(".navigation > ul")
          .find("li.dropdown2")
          .removeClass("open");
        $(this)
          .parents(".navigation > ul")
          .find("li.dropdown2 > ul")
          .slideUp(500);
        $(this).parent("li").toggleClass("open");
        $(this).parent("li").children("ul").slideToggle(500);
      }
    });

    //Menu Toggle Btn
    $(".mobile-nav-toggler").on("click", function () {
      $("body").addClass("mobile-menu-visible");
    });

    //Menu Toggle Btn
    $(".mobile-menu .menu-backdrop, .close-btn").on("click", function () {
      $("body").removeClass("mobile-menu-visible");
      $(".mobile-menu .navigation > li").removeClass("open");
      $(".mobile-menu .navigation li ul").slideUp(0);
    });

    $(document).keydown(function (e) {
      if (e.keyCode === 27) {
        $("body").removeClass("mobile-menu-visible");
        $(".mobile-menu .navigation > li").removeClass("open");
        $(".mobile-menu .navigation li ul").slideUp(0);
      }
    });
  }

  /* alert box
  ------------------------------------------------------------------------------------- */
  var alertBox = function () {
    $(document).on("click", ".close", function (e) {
      $(this).closest(".flat-alert").remove();
      e.preventDefault();
    });
  };

  /* footer accordion
  -------------------------------------------------------------------------*/
  var handleFooter = function () {
    var footerAccordion = function () {
      var args = { duration: 250 };
      $(".footer-heading-mobile").on("click", function () {
        $(this).parent(".footer-col-block").toggleClass("open");
        if (!$(this).parent(".footer-col-block").is(".open")) {
          $(this).next().slideUp(args);
        } else {
          $(this).next().slideDown(args);
        }
      });
    };
    function handleAccordion() {
      if (matchMedia("only screen and (max-width: 767px)").matches) {
        if (!$(".footer-heading-mobile").data("accordion-initialized")) {
          footerAccordion();
          $(".footer-heading-mobile").data("accordion-initialized", true);
        }
      } else {
        $(".footer-heading-mobile").off("click");
        $(".footer-heading-mobile")
          .parent(".footer-col-block")
          .removeClass("open");
        $(".footer-heading-mobile").next().removeAttr("style");
        $(".footer-heading-mobile").data("accordion-initialized", false);
      }
    }
    handleAccordion();
    window.addEventListener("resize", function () {
      handleAccordion();
    });
  };

  // Dom Ready
  $(function () {
    $(window).on("load resize", function () {
      retinaLogos();
    });
    headerFixed();
    alertBox();
    handleFooter();
  });
})(jQuery);
