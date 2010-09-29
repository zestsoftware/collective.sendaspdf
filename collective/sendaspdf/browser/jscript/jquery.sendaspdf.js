/*
 * Contains the various Jquery bindings used to send the page as PDF.
 * We wait the document to be ready so we are sure that the jquery.pyproxy
 * library has been loaded.
 */

jQuery(document).ready(function() {
    (function($) {
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

	/* Checks all forms elements and sets their
	 * values in HTML.
	 */
	function update_form_fields() {
	    $('input:checked[type=checkbox]').each(function() {
		/* Ok, this looks silly, but $(':checked').attr('checked', 'checked')
		 * does not update the cjeck attribute.
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
	    
	    /* The list of test types. */
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
	function show_send_form (e) {
	    e.preventDefault();
	    $.pyproxy_call('jq_get_send_as_pdf_form',
			   {page: get_page_source() })
	};
	
	/* Bind the send_as_pdf link with a pyproxy call.
	 * XXX - I do not like the selection based on the URL,
	 * so if you have a solution to give an ID or at least
	 * a CSS class to a portal_action, feel free to help :)
	 */
	$('.documentActions a[href*=send_as_pdf?page_url=]').live(
	    'click', show_send_form);
    })(jQuery)
});