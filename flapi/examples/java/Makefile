ROOT := $(dir $(firstword $(MAKEFILE_LIST)))
JAVA := /usr/bin/java
JAVAC := /usr/bin/javac -g
CLASSPATH := "/usr/fl/baselight-5.3.17711/share/flapi/java/*"
QUIET ?= @

SRCS := $(shell ls $(ROOT)/*.java)
OBJS := $(SRCS:.java=.class)

all: $(OBJS)
%.class: %.java
	@echo Compiling $(notdir $^)
	$(QUIET)$(JAVAC) -Xlint:unchecked -cp $(CLASSPATH) -d $(ROOT) $^

clean:
	@echo Cleaning up
	$(QUIET)rm -f $(OBJS)
