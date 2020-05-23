#!/usr/bin/env python3
# coding: utf8
# 20170315 anChaOs

from app import celery

def main():
    args = ['worker', '--loglevel=info', '--concurrency=30', '-n mafu_worker']
    celery.worker_main(args)


if __name__ == '__main__':
    main()