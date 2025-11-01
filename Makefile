# Compiler and flags
CXX = g++
CXXFLAGS = -std=c++17 -pthread -Wall -Wextra -O2
LDFLAGS = -pthread

# Targets
SERVER_TARGET = server
CLIENT_TARGET = client

# Source files
SERVER_SOURCES = server.cpp config.cpp protocol.cpp scheduler.cpp utils.cpp
CLIENT_SOURCES = client.cpp config.cpp protocol.cpp utils.cpp

# Object files
SERVER_OBJECTS = $(SERVER_SOURCES:.cpp=.o)
CLIENT_OBJECTS = $(CLIENT_SOURCES:.cpp=.o)

# Default target
all: $(SERVER_TARGET) $(CLIENT_TARGET)

# Server target
$(SERVER_TARGET): $(SERVER_OBJECTS)
	$(CXX) $(LDFLAGS) -o $@ $^

# Client target
$(CLIENT_TARGET): $(CLIENT_OBJECTS)
	$(CXX) $(LDFLAGS) -o $@ $^

# Compile source files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Dependencies
config.o: config.cpp config.h
protocol.o: protocol.cpp protocol.h
scheduler.o: scheduler.cpp scheduler.h protocol.h
utils.o: utils.cpp utils.h
server.o: server.cpp config.h protocol.h scheduler.h utils.h
client.o: client.cpp config.h protocol.h utils.h

# Clean
clean:
	rm -f $(SERVER_OBJECTS) $(CLIENT_OBJECTS) $(SERVER_TARGET) $(CLIENT_TARGET)
	rm -f *.o
	rm -f metrics.csv
	rm -f output_* downloaded_*

# Clean all generated files
clean-all: clean
	rm -rf testdata/
	rm -f *.csv *.png

# Help
help:
	@echo "Available targets:"
	@echo "  all          - Build both server and client (default)"
	@echo "  server       - Build server only"
	@echo "  client       - Build client only"
	@echo "  clean        - Remove build artifacts"
	@echo "  clean-all    - Remove all generated files"
	@echo "  help         - Show this help message"

.PHONY: all clean clean-all help
