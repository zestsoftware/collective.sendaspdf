/*
 * Contains the various Jquery bindings used to send the page as PDF.
 * We wait the document to be ready so we are sure that the jquery.pyproxy
 * library has been loaded.
 */

jQuery(document).ready(function() {
    (function($) {
	if (typeof($().pyproxy) != 'function') {
	    /* jquery.pyproxy javascript file has not been set correctly.*/
	    return;
	}

	function submit_send_form(e) {
	    e.preventDefault();

	    if (typeof(tinymce) != 'indefined') {
		tinymce.EditorManager.activeEditor.save();
	    }

	    $.pyproxy_call('jq_send_as_pdf', '#send_as_pdf_popup');
	};

	/* Plone 3 is using jQuery 1.2, so we can not use parentUntil which
	 * was defined in jQuery 1.4.
	 * This method will give an equivalent of $('bla').parentUntil('form')
	 */
	$.fn.findForm = function() {
	    var parent = $(this);
	    var found = false;

	    while (!found) {
		parent = parent.parent();
		if (parent.length == 0) {
		    found = true;
		    break;
		}
		found = (parent[0].nodeName.toLowerCase() == 'form');
	    }
	    return parent;
	}

	$.fn.redirect = function(url) {
	    window.location = url;
	}

	/* Custom simple lightbox.
	 */
	$.fn.send_as_pdf_lightbox = function() {
	    function close_lightbox(e) {
		e.preventDefault();
		$('#send_as_pdf_lighbox_background').hide();
		$('#send_as_pdf_popup').remove();
	    }

	    /* Create a background */
	    $('body').append('<div id="send_as_pdf_lighbox_background"></div>');
	    $('#send_as_pdf_lighbox_background').
		css({width: $(document).width() + 'px',
		     height: $(document).height() + 'px'
		    }).
		show();

	    /* Close the lightbox when hitting 'ESC' */
	    $(document).keyup(function(e) {
		if (e.keyCode == 27) {
		    close_lightbox(e);
		}
	    });

	    return $(this).each(function() {
		var element = $(this);

		$(this).css({
		    top: ($(window).scrollTop() + 10) + 'px',
		    right: (($(document).width() - 500) / 2) + 'px'
		});
		     
		element.find('input[name=form_cancelled]').click(close_lightbox);
		element.find('a.send_as_pdf_close').live('click', close_lightbox);

		element.find('input[name=form_submitted]').live('click',
								submit_send_form);
	    });
	}

	/* Checks all forms elements and sets their
	 * values in HTML.
	 */
	function update_form_fields() {
	    $('input:checked[type=checkbox]').each(function() {
		/* Ok, this looks silly, but $(':checked').attr('checked', 'checked')
		 * does not update the check attribute.
		 * jQuery is a bit too smart here...
		 */
		this.setAttribute('checked', 'checked');
	    });

	    $('input:checked[type=radio]').each(function() {
		/* For the radio buttons we also need to uncheck
		   those which might be checked. */
		$(this).
		    findForm().
		    find('input[type=radio][name=' + this.name + ']').
		    each(function() {
			this.removeAttribute('checked');
		    });
	    });

	    $('option:selected').each(function() {
		/* We remove the other one that might be selected. */
		$(this).parent().find('option').each(function() {
		    this.removeAttribute('selected');
		});
		this.setAttribute('selected', 'selected');
	    });
	    
	    /* The list of text input. */
	    var text_types = ['text', 'email', 'url', 'number', 'range', 'search', 'color'];
	    for (i=0; i<text_types.length; i++) {
		$('input[type=' + text_types[i] + ']').each(
		    function() {
			this.setAttribute('value', this.value);
		    });
	    }
	}

	/* Gets the current's page source code */
	function get_page_source() {
	    update_form_fields();

	    var base, source, i;
	    base = $('html');
	    source = '<html';
	    
	    for (i = 0; i < base[0].attributes.length; i++) {
		source += ' ' + base[0].attributes[i].name + '="' + base[0].attributes[i].value + '"';
	    }
	    
	    source += '>' + base.html() + '</html>';
	    return source;
	}
	
	/* Gets the content of the current page and sends it
	   using pyproxy to the server so it generates the pdf. */
	function show_send_form(e) {
	    e.preventDefault();
	    $.pyproxy_call('jq_get_send_as_pdf_form',
			   {page: get_page_source() },
			   function() {
			       if ($('#field_text').length == 0) {
				   /* The form did not load correctly (for example missconfiguration
				    of wkhtmltopdf), we can not start editors.*/
				   return;
			       }
			       /* Load TinyMCE */
			       if (typeof(TinyMCEConfig) != 'undefined') {
				   var config = new TinyMCEConfig('text');
				   config.init();
			       }
			   })
	};

	function download_pdf(e) {
	    e.preventDefault();
	    $.pyproxy_call('jq_download_as_pdf',
			   {page: get_page_source() })
	};

	
	/* Bind the send_as_pdf link with a pyproxy call.
	 * XXX - I do not like the selection based on the URL,
	 * so if you have a solution to give an ID or at least
	 * a CSS class to a portal_action, feel free to help :)
	 */
	$('.documentActions a[href*=send_as_pdf?page_url=]').click(show_send_form);
	$('.documentActions a[href*=download_as_pdf?page_url=]').click(download_pdf);
    })(jQuery)
});