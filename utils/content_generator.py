"""Content generation utilities for SharePoint MCP server."""

import logging
from typing import Dict, Any

# Setup logging
logger = logging.getLogger("content_generator")


class ContentGenerator:
    """Generator for AI-enhanced content."""

    @staticmethod
    def generate_page_content(
        purpose: str, title: str, audience: str = "general"
    ) -> Dict[str, Any]:
        """Generate page content based on purpose and audience.

        Args:
            purpose: Purpose of the page (article, dashboard, landing, etc.)
            title: Title of the page
            audience: Target audience (general, executives, team, customers, etc.)

        Returns:
            Dictionary with generated content sections
        """
        # In a real implementation, this could call an LLM to generate content
        # For now, we'll use predefined templates based on purpose and audience

        if purpose.lower() == "welcome":
            return ContentGenerator._generate_welcome_page(title, audience)
        elif purpose.lower() == "dashboard":
            return ContentGenerator._generate_dashboard_page(title, audience)
        elif purpose.lower() == "team":
            return ContentGenerator._generate_team_page(title, audience)
        elif purpose.lower() == "project":
            return ContentGenerator._generate_project_page(title, audience)
        elif purpose.lower() == "announcement":
            return ContentGenerator._generate_announcement_page(title, audience)
        else:
            return ContentGenerator._generate_general_page(title, audience)

    @staticmethod
    def _generate_welcome_page(title: str, audience: str) -> Dict[str, Any]:
        """Generate a welcome page.

        Args:
            title: Page title
            audience: Target audience

        Returns:
            Content for a welcome page
        """
        # Adjust content based on audience
        intro_text = ""
        main_content = ""

        if audience.lower() == "executives":
            intro_text = "Welcome to our executive portal. This site provides access to strategic resources and key performance indicators to help guide decision-making."
            main_content = """
## Strategic Resources

Access the latest executive briefings, board presentations, and strategic planning documents.

## Key Performance Indicators

Review real-time dashboards showing organizational performance across all business units.

## Upcoming Executive Events

Stay informed about upcoming board meetings, executive retreats, and leadership events.
"""
        elif audience.lower() == "team":
            intro_text = "Welcome to our team site! This is your central hub for collaboration, resources, and team updates."
            main_content = """
## Team Resources

Find templates, guidelines, and shared resources to help you in your daily work.

## Team Calendar

Stay up-to-date with team events, deadlines, and important milestones.

## Team News

Catch up on the latest team announcements, achievements, and updates.
"""
        elif audience.lower() == "customers":
            intro_text = "Welcome to our customer portal. We're glad you're here and look forward to supporting your needs."
            main_content = """
## Support Resources

Access guides, FAQs, and troubleshooting resources to help you get the most out of our products.

## Latest Updates

Stay informed about new features, updates, and improvements to our products and services.

## Contact Us

Find the right contact information for your specific needs and questions.
"""
        else:  # General audience
            intro_text = "Welcome to our SharePoint site. This is your gateway to information, resources, and collaboration tools."
            main_content = """
## Featured Resources

Discover the most popular and useful resources available on this site.

## Recent Updates

Stay informed about the latest news, announcements, and updates.

## Quick Links

Access frequently used tools and resources with just one click.
"""

        return {
            "title": title,
            "introduction": intro_text,
            "main_content": main_content,
            "conclusion": "Thank you for visiting. Please explore the site and don't hesitate to provide feedback.",
            "layout_suggestion": "SingleColumnWithHeader",
            "image_suggestions": {
                "url": "/api/placeholder/800/400",
                "alt_text": "Welcome banner image",
            },
        }

    @staticmethod
    def _generate_dashboard_page(title: str, audience: str) -> Dict[str, Any]:
        """Generate a dashboard page.

        Args:
            title: Page title
            audience: Target audience

        Returns:
            Content for a dashboard page
        """
        intro_text = "This dashboard provides a comprehensive view of key metrics and information."

        # Adjust content based on audience
        if audience.lower() == "executives":
            main_content = """
## Performance Metrics

<div class="dashboard-section">
    <div class="metric-card">
        <h3>Revenue</h3>
        <p class="metric-value">$10.2M</p>
        <p class="metric-trend">↑ 12.5%</p>
    </div>
    <div class="metric-card">
        <h3>Costs</h3>
        <p class="metric-value">$6.8M</p>
        <p class="metric-trend">↓ 3.2%</p>
    </div>
    <div class="metric-card">
        <h3>Profit Margin</h3>
        <p class="metric-value">33.4%</p>
        <p class="metric-trend">↑ 5.1%</p>
    </div>
</div>

## Strategic Initiatives

<div class="progress-section">
    <div class="progress-item">
        <h3>Digital Transformation</h3>
        <div class="progress-bar" style="width: 75%;">75%</div>
    </div>
    <div class="progress-item">
        <h3>Market Expansion</h3>
        <div class="progress-bar" style="width: 40%;">40%</div>
    </div>
    <div class="progress-item">
        <h3>Operational Excellence</h3>
        <div class="progress-bar" style="width: 60%;">60%</div>
    </div>
</div>
"""
        elif audience.lower() == "team":
            main_content = """
## Team Metrics

<div class="dashboard-section">
    <div class="metric-card">
        <h3>Tasks Completed</h3>
        <p class="metric-value">42</p>
        <p class="metric-trend">↑ 8</p>
    </div>
    <div class="metric-card">
        <h3>Tasks In Progress</h3>
        <p class="metric-value">15</p>
    </div>
    <div class="metric-card">
        <h3>Upcoming Deadlines</h3>
        <p class="metric-value">7</p>
    </div>
</div>

## Team Workload

<div class="progress-section">
    <div class="progress-item">
        <h3>Project Alpha</h3>
        <div class="progress-bar" style="width: 65%;">65%</div>
    </div>
    <div class="progress-item">
        <h3>Project Beta</h3>
        <div class="progress-bar" style="width: 30%;">30%</div>
    </div>
    <div class="progress-item">
        <h3>Ongoing Support</h3>
        <div class="progress-bar" style="width: 85%;">85%</div>
    </div>
</div>
"""
        else:
            main_content = """
## Key Metrics

<div class="dashboard-section">
    <div class="metric-card">
        <h3>Active Projects</h3>
        <p class="metric-value">12</p>
    </div>
    <div class="metric-card">
        <h3>Recent Documents</h3>
        <p class="metric-value">24</p>
    </div>
    <div class="metric-card">
        <h3>Team Members</h3>
        <p class="metric-value">15</p>
    </div>
</div>

## Status Overview

<div class="progress-section">
    <div class="progress-item">
        <h3>Overall Progress</h3>
        <div class="progress-bar" style="width: 55%;">55%</div>
    </div>
    <div class="progress-item">
        <h3>Budget Utilization</h3>
        <div class="progress-bar" style="width: 40%;">40%</div>
    </div>
    <div class="progress-item">
        <h3>Timeline Adherence</h3>
        <div class="progress-bar" style="width: 70%;">70%</div>
    </div>
</div>
"""

        return {
            "title": title,
            "introduction": intro_text,
            "main_content": main_content,
            "conclusion": "This dashboard is updated regularly. Last update: Today",
            "layout_suggestion": "Dashboard",
            "image_suggestions": None,
        }

    @staticmethod
    def _generate_team_page(title: str, audience: str) -> Dict[str, Any]:
        """Generate a team page.

        Args:
            title: Page title
            audience: Target audience

        Returns:
            Content for a team page
        """
        intro_text = "Meet our talented team of professionals dedicated to excellence and innovation."

        main_content = """
## Leadership Team

<div class="team-grid">
    <div class="team-member">
        <img src="/api/placeholder/200/200" alt="Team Member" />
        <h3>Jane Smith</h3>
        <p>Chief Executive Officer</p>
    </div>
    <div class="team-member">
        <img src="/api/placeholder/200/200" alt="Team Member" />
        <h3>John Davis</h3>
        <p>Chief Technology Officer</p>
    </div>
    <div class="team-member">
        <img src="/api/placeholder/200/200" alt="Team Member" />
        <h3>Sarah Johnson</h3>
        <p>Chief Operations Officer</p>
    </div>
</div>

## Development Team

<div class="team-grid">
    <div class="team-member">
        <img src="/api/placeholder/200/200" alt="Team Member" />
        <h3>Michael Chen</h3>
        <p>Lead Developer</p>
    </div>
    <div class="team-member">
        <img src="/api/placeholder/200/200" alt="Team Member" />
        <h3>Emily Rodriguez</h3>
        <p>UX Designer</p>
    </div>
    <div class="team-member">
        <img src="/api/placeholder/200/200" alt="Team Member" />
        <h3>David Kim</h3>
        <p>Full Stack Developer</p>
    </div>
</div>

## Marketing Team

<div class="team-grid">
    <div class="team-member">
        <img src="/api/placeholder/200/200" alt="Team Member" />
        <h3>Lisa Wang</h3>
        <p>Marketing Director</p>
    </div>
    <div class="team-member">
        <img src="/api/placeholder/200/200" alt="Team Member" />
        <h3>James Wilson</h3>
        <p>Content Strategist</p>
    </div>
    <div class="team-member">
        <img src="/api/placeholder/200/200" alt="Team Member" />
        <h3>Olivia Martinez</h3>
        <p>Social Media Manager</p>
    </div>
</div>
"""

        return {
            "title": title,
            "introduction": intro_text,
            "main_content": main_content,
            "conclusion": "We believe in teamwork, innovation, and delivering exceptional results.",
            "layout_suggestion": "FullWidth",
            "image_suggestions": {
                "url": "/api/placeholder/1200/400",
                "alt_text": "Team working together",
            },
        }

    @staticmethod
    def _generate_project_page(title: str, audience: str) -> Dict[str, Any]:
        """Generate a project page.

        Args:
            title: Page title
            audience: Target audience

        Returns:
            Content for a project page
        """
        intro_text = f"Welcome to the {title} project page. Here you'll find all the essential information about this project."

        main_content = """
## Project Overview

This project aims to deliver [project objective] by [target date]. The initiative will focus on addressing [key challenges] and providing [main benefits].

## Project Timeline

<div class="timeline">
    <div class="timeline-item">
        <h3>Project Initiation</h3>
        <p>Completed: April 1, 2025</p>
        <ul>
            <li>Defined project scope</li>
            <li>Assembled project team</li>
            <li>Secured initial funding</li>
        </ul>
    </div>
    <div class="timeline-item current">
        <h3>Planning Phase</h3>
        <p>In Progress: April 15 - May 30, 2025</p>
        <ul>
            <li>Creating detailed requirements</li>
            <li>Developing project plan</li>
            <li>Resource allocation</li>
        </ul>
    </div>
    <div class="timeline-item">
        <h3>Implementation</h3>
        <p>Upcoming: June 1 - August 15, 2025</p>
        <ul>
            <li>Development work</li>
            <li>Regular testing cycles</li>
            <li>Stakeholder reviews</li>
        </ul>
    </div>
    <div class="timeline-item">
        <h3>Deployment</h3>
        <p>Planned: August 15 - September 15, 2025</p>
        <ul>
            <li>Final testing</li>
            <li>User training</li>
            <li>Production deployment</li>
        </ul>
    </div>
</div>

## Key Resources

<div class="resources-grid">
    <div class="resource-item">
        <h3>Project Charter</h3>
        <p>Detailed project scope and objectives</p>
        <a href="#">View Document</a>
    </div>
    <div class="resource-item">
        <h3>Requirements Doc</h3>
        <p>Comprehensive project requirements</p>
        <a href="#">View Document</a>
    </div>
    <div class="resource-item">
        <h3>Project Plan</h3>
        <p>Timeline, milestones, and assignments</p>
        <a href="#">View Document</a>
    </div>
</div>

## Project Team

<ul>
    <li><strong>Project Sponsor:</strong> [Name], [Title]</li>
    <li><strong>Project Manager:</strong> [Name], [Title]</li>
    <li><strong>Key Team Members:</strong> [Names and Roles]</li>
</ul>
"""

        return {
            "title": title,
            "introduction": intro_text,
            "main_content": main_content,
            "conclusion": "For questions about this project, please contact the project manager.",
            "layout_suggestion": "TwoColumns",
            "image_suggestions": {
                "url": "/api/placeholder/600/400",
                "alt_text": "Project visualization",
            },
        }

    @staticmethod
    def _generate_announcement_page(title: str, audience: str) -> Dict[str, Any]:
        """Generate an announcement page.

        Args:
            title: Page title
            audience: Target audience

        Returns:
            Content for an announcement page
        """
        intro_text = "We have an important announcement to share with our organization."

        main_content = """
## Announcement Details

We are pleased to announce [key announcement]. This [change/update/initiative] represents an important development for our organization and will [describe impact].

## Key Points

- [Key point 1]
- [Key point 2]
- [Key point 3]
- [Key point 4]

## What This Means For You

This announcement will impact [describe who is affected] in the following ways:

1. [Impact 1]
2. [Impact 2]
3. [Impact 3]

## Next Steps

In the coming weeks, we will be:

- [Next step 1]
- [Next step 2]
- [Next step 3]

## Questions?

If you have questions about this announcement, please:

- Attend our upcoming Town Hall on [date] at [time]
- Contact [name/department] at [contact information]
- Review the FAQ document [link]
"""

        return {
            "title": title,
            "introduction": intro_text,
            "main_content": main_content,
            "conclusion": "Thank you for your attention to this important announcement.",
            "layout_suggestion": "SingleColumnCentered",
            "image_suggestions": {
                "url": "/api/placeholder/800/300",
                "alt_text": "Announcement illustration",
            },
        }

    @staticmethod
    def _generate_general_page(title: str, audience: str) -> Dict[str, Any]:
        """Generate a general purpose page.

        Args:
            title: Page title
            audience: Target audience

        Returns:
            Content for a general page
        """
        intro_text = f"Welcome to the {title} page. This page provides information and resources related to {title}."

        main_content = """
## Overview

This section provides an overview of key information related to this topic.

## Key Resources

<div class="resources-grid">
    <div class="resource-item">
        <h3>Documents</h3>
        <p>Access important documents and files</p>
        <a href="#">View Documents</a>
    </div>
    <div class="resource-item">
        <h3>Links</h3>
        <p>Useful links and references</p>
        <a href="#">View Links</a>
    </div>
    <div class="resource-item">
        <h3>Tools</h3>
        <p>Helpful tools and applications</p>
        <a href="#">Access Tools</a>
    </div>
</div>

## Recent Updates

<div class="updates-list">
    <div class="update-item">
        <h3>Update Title 1</h3>
        <p class="date">April 5, 2025</p>
        <p>Brief description of the update and its significance.</p>
    </div>
    <div class="update-item">
        <h3>Update Title 2</h3>
        <p class="date">March 28, 2025</p>
        <p>Brief description of the update and its significance.</p>
    </div>
    <div class="update-item">
        <h3>Update Title 3</h3>
        <p class="date">March 15, 2025</p>
        <p>Brief description of the update and its significance.</p>
    </div>
</div>
"""

        return {
            "title": title,
            "introduction": intro_text,
            "main_content": main_content,
            "conclusion": "Thank you for visiting this page. It was last updated on April 9, 2025.",
            "layout_suggestion": "TwoThirdsOneThird",
            "image_suggestions": {
                "url": "/api/placeholder/800/300",
                "alt_text": "Illustrative image for " + title,
            },
        }

    @staticmethod
    def generate_page_title(purpose: str, name: str) -> str:
        """Generate an appropriate page title based on purpose and name.

        Args:
            purpose: Purpose of the page
            name: Base name for the page

        Returns:
            Generated title
        """
        purpose_prefixes = {
            "welcome": "Welcome to the ",
            "dashboard": "",
            "team": "Meet Our ",
            "project": "",
            "announcement": "Announcement: ",
            "report": "Report: ",
            "guide": "Guide: ",
            "policy": "Policy: ",
            "training": "Training: ",
        }

        purpose_suffixes = {
            "welcome": " Site",
            "dashboard": " Dashboard",
            "team": " Team",
            "project": " Project",
            "announcement": "",
            "report": " Summary",
            "guide": " Guide",
            "policy": " Policy",
            "training": " Training Materials",
        }

        prefix = purpose_prefixes.get(purpose.lower(), "")
        suffix = purpose_suffixes.get(purpose.lower(), "")

        # Clean the name and capitalize words
        clean_name = " ".join(word.capitalize() for word in name.strip().split())

        return f"{prefix}{clean_name}{suffix}"

    @staticmethod
    def map_purpose_to_template(purpose: str) -> str:
        """Map page purpose to an appropriate template.

        Args:
            purpose: Purpose of the page

        Returns:
            Template name suitable for the purpose
        """
        purpose_templates = {
            "welcome": "HomeWelcome",
            "dashboard": "Dashboard",
            "team": "TeamDisplay",
            "project": "ProjectOverview",
            "announcement": "Announcement",
            "report": "Report",
            "guide": "Guide",
            "policy": "Article",
            "training": "Training",
        }

        return purpose_templates.get(purpose.lower(), "Article")
