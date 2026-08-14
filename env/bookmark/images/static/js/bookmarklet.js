(function(){
  var jquery_version = '3.4.1';
  var site_url = 'http://127.0.0.1:8000/';
  var static_url = site_url + 'static/';
  var min_width = 100;
  var min_height = 100;

  function bookmarklet(msg) {
    // Load CSS
    var css = jQuery('<link>');
    css.attr({
      rel: 'stylesheet',
      type: 'text/css',
      href: static_url + 'css/bookmarklet.css?r=' + Math.floor(Math.random()*99999999999999999999)
    });
    jQuery('head').append(css);

    // Load HTML
    var box_html = '<div id="bookmarklet"><a href="#" id="close">&times;</a><h1>Select an image to bookmark:</h1><div class="images"></div></div>';
    jQuery('body').append(box_html);

    // Close event
    jQuery('#bookmarklet #close').click(function(){
      jQuery('#bookmarklet').remove();
    });

    // Find images and display them
    var found_images = 0;
    jQuery('img').each(function(index, image) {
      var src = image.src || jQuery(image).attr('src');
      if (src && (image.naturalWidth >= min_width || jQuery(image).width() >= min_width) && (image.naturalHeight >= min_height || jQuery(image).height() >= min_height)) {
        if (src.match(/\.(jpeg|jpg|png|webp)($|\?)/i) || src.startsWith('http')) {
          found_images++;
          jQuery('#bookmarklet .images').append('<a href="#"><img src="'+ src +'" /></a>');
        }
      }
    });

    if (found_images === 0) {
      jQuery('#bookmarklet .images').append('<p style="color: #64748b; font-size: 13px; margin: 8px 0;">No images (≥100px) found on this page.</p>');
    }

    // When an image is selected, open create URL
    jQuery('#bookmarklet .images a').click(function(e){
      var selected_image = jQuery(this).children('img').attr('src');
      jQuery('#bookmarklet').hide();
      window.open(site_url + 'images/create/?url='
        + encodeURIComponent(selected_image)
        + '&title='
        + encodeURIComponent(jQuery('title').text()),
        '_blank');
    });
  }

  // Check if jQuery is loaded
  if(typeof window.jQuery != 'undefined') {
    bookmarklet();
  } else {
    var script = document.createElement('script');
    script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/' + jquery_version + '/jquery.min.js';
    document.head.appendChild(script);
    var attempts = 15;
    (function(){
      if(typeof window.jQuery == 'undefined') {
        if(--attempts > 0) {
          window.setTimeout(arguments.callee, 250);
        } else {
          alert('An error occurred while loading jQuery');
        }
      } else {
        bookmarklet();
      }
    })();
  }
})();
