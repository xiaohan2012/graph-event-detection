all: 
	rm -rf /cs/home/hxiao/public_html/figures/
	cp -r figures/ /cs/home/hxiao/public_html
	chmod -R a+xr /cs/home/hxiao/public_html/figures

# all:
# 	rm -rf /cs/home/hxiao/public_html/event_html/
# 	cp -r html/ /cs/home/hxiao/public_html/event_html/
# 	chmod -R a+xr /cs/home/hxiao/public_html/event_html
