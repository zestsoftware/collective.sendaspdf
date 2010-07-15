/*
 * Contains the various Jquery bindings used to send the page as PDF.
 */

(function($) {
    /* Gets the current's page source code */
    function get_page_source() {
	var base, source, i;
	base = $('html');
	source = '<html';

	for (i = 0; i < base[0].attributes.length; i++) {
	    source += ' ' + base[0].attributes[i].name + '="' + base[0].attributes[i].value + '"';
	}

	source += '>' + base.html() + '</html>';
	return source;
    }
})(jQuery)