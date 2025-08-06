#!/bin/bash

coverage run --omit='test/*,actions/HomeAssistantAction/*' -m unittest; coverage html
