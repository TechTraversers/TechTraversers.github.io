// Allow only Clarity's script URLs through the existing Trusted Types enforcement.
if (window.trustedTypes) {
    window.trustedTypes.createPolicy('default', {
        createScriptURL: function(url) {
            if (url === 'https://www.clarity.ms/tag/yzgnnv7sl9' ||
                /^https:\/\/scripts\.clarity\.ms\/\d+\.\d+\.\d+\/clarity\.js$/.test(url)) {
                return url;
            }
            throw new TypeError('Unapproved script URL');
        }
    });
}
(function(c,l,a,r,i,t,y){
    c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
    t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
    y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
})(window, document, "clarity", "script", "yzgnnv7sl9");
