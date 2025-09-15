#!/usr/bin/env python3
"""
Populate RAG Database with Sample Documents
This script populates the ChromaDB vector database with sample project management documents
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.vector_db import get_vector_db, Document
from app.core.logging import get_logger

logger = get_logger("scripts.populate_rag_database")

# Sample documents for RAG database
SAMPLE_DOCUMENTS = {
    "projects": [
        {
            "content": """
            Project Management Best Practices:
            
            1. Define Clear Objectives: Every project should have well-defined, measurable objectives that align with business goals.
            
            2. Create Detailed Project Plans: Develop comprehensive project plans including timelines, milestones, and resource allocation.
            
            3. Risk Management: Identify potential risks early and develop mitigation strategies. Regular risk assessments should be conducted throughout the project lifecycle.
            
            4. Communication: Maintain clear and consistent communication with all stakeholders. Regular status updates and meetings are essential.
            
            5. Quality Assurance: Implement quality control processes to ensure deliverables meet requirements and standards.
            
            6. Resource Management: Efficiently allocate and manage resources including personnel, budget, and equipment.
            
            7. Change Management: Establish processes for handling scope changes and ensure proper approval workflows.
            
            8. Documentation: Maintain comprehensive project documentation including decisions, changes, and lessons learned.
            """,
            "metadata": {
                "project_id": "PM-001",
                "name": "Project Management Best Practices",
                "status": "Active",
                "priority": "High",
                "type": "Knowledge Base",
                "category": "Best Practices",
                "author": "Project Management Office",
                "version": "1.0",
                "created_at": "2024-01-15"
            }
        },
        {
            "content": """
            Agile Project Management Methodology:
            
            Agile is an iterative approach to project management that emphasizes flexibility, collaboration, and rapid delivery of value.
            
            Key Principles:
            - Individuals and interactions over processes and tools
            - Working software over comprehensive documentation
            - Customer collaboration over contract negotiation
            - Responding to change over following a plan
            
            Common Agile Frameworks:
            1. Scrum: Uses sprints (2-4 week iterations) with daily standups, sprint planning, and retrospectives
            2. Kanban: Focuses on continuous delivery with visual workflow management
            3. Lean: Emphasizes eliminating waste and maximizing value delivery
            4. Extreme Programming (XP): Focuses on technical excellence and customer satisfaction
            
            Benefits:
            - Faster time to market
            - Better customer satisfaction
            - Improved team collaboration
            - Higher quality deliverables
            - Better risk management
            """,
            "metadata": {
                "project_id": "AG-001",
                "name": "Agile Project Management Guide",
                "status": "Active",
                "priority": "High",
                "type": "Methodology",
                "category": "Agile",
                "author": "Agile Coach",
                "version": "2.1",
                "created_at": "2024-01-20"
            }
        },
        {
            "content": """
            Risk Management Framework:
            
            Risk management is a critical component of project management that involves identifying, assessing, and mitigating potential threats to project success.
            
            Risk Categories:
            1. Technical Risks: Technology failures, integration issues, performance problems
            2. Business Risks: Market changes, stakeholder conflicts, budget constraints
            3. Resource Risks: Staff unavailability, skill gaps, equipment failures
            4. External Risks: Regulatory changes, vendor issues, natural disasters
            5. Schedule Risks: Delays, dependencies, scope creep
            
            Risk Assessment Process:
            1. Risk Identification: Brainstorm potential risks using various techniques
            2. Risk Analysis: Evaluate probability and impact of each risk
            3. Risk Prioritization: Rank risks based on severity and urgency
            4. Risk Response Planning: Develop mitigation strategies
            5. Risk Monitoring: Continuously track and update risk status
            
            Risk Response Strategies:
            - Avoid: Eliminate the risk entirely
            - Mitigate: Reduce probability or impact
            - Transfer: Shift risk to third party (insurance, contracts)
            - Accept: Acknowledge and monitor the risk
            """,
            "metadata": {
                "project_id": "RM-001",
                "name": "Risk Management Framework",
                "status": "Active",
                "priority": "High",
                "type": "Framework",
                "category": "Risk Management",
                "author": "Risk Management Team",
                "version": "1.5",
                "created_at": "2024-01-25"
            }
        }
    ],
    "features": [
        {
            "content": """
            AI-Powered Project Analytics Feature:
            
            This feature provides intelligent insights and predictions for project management using machine learning algorithms.
            
            Capabilities:
            1. Predictive Analytics: Forecast project completion dates, budget overruns, and resource needs
            2. Risk Prediction: Identify potential risks before they become issues
            3. Resource Optimization: Suggest optimal resource allocation based on project requirements
            4. Performance Benchmarking: Compare project performance against industry standards
            5. Automated Reporting: Generate comprehensive project reports with AI-generated insights
            
            Technical Implementation:
            - Machine Learning Models: Use historical project data to train predictive models
            - Real-time Processing: Analyze project data in real-time for immediate insights
            - Natural Language Processing: Generate human-readable reports and recommendations
            - Integration APIs: Connect with existing project management tools
            
            Benefits:
            - Improved decision making through data-driven insights
            - Proactive risk management and issue prevention
            - Optimized resource utilization and cost management
            - Enhanced project success rates and stakeholder satisfaction
            """,
            "metadata": {
                "feature_id": "AI-001",
                "name": "AI-Powered Project Analytics",
                "project_id": "AI-PROJECT",
                "status": "In Development",
                "complexity": "High",
                "priority": "Critical",
                "category": "AI Features",
                "author": "AI Development Team",
                "version": "0.8",
                "created_at": "2024-02-01"
            }
        },
        {
            "content": """
            Real-time Collaboration Dashboard:
            
            A comprehensive dashboard that enables real-time collaboration and communication among project team members.
            
            Features:
            1. Live Updates: Real-time synchronization of project data across all team members
            2. Interactive Charts: Dynamic visualizations that update automatically
            3. Team Chat: Integrated messaging system for project communication
            4. File Sharing: Secure document sharing and version control
            5. Task Management: Real-time task assignment and status updates
            6. Notification System: Smart notifications for important events and deadlines
            
            Technical Specifications:
            - WebSocket Integration: Real-time bidirectional communication
            - Responsive Design: Works seamlessly across desktop and mobile devices
            - Security: End-to-end encryption for sensitive project data
            - Scalability: Supports large teams and complex project structures
            
            User Experience:
            - Intuitive Interface: Easy-to-use design for all skill levels
            - Customizable Views: Personalized dashboards based on user roles
            - Accessibility: WCAG 2.1 compliant for inclusive access
            - Performance: Fast loading times and smooth interactions
            """,
            "metadata": {
                "feature_id": "RT-001",
                "name": "Real-time Collaboration Dashboard",
                "project_id": "COLLAB-PROJECT",
                "status": "Active",
                "complexity": "Medium",
                "priority": "High",
                "category": "Collaboration",
                "author": "UX Development Team",
                "version": "2.0",
                "created_at": "2024-01-30"
            }
        }
    ],
    "documentation": [
        {
            "content": """
            API Documentation - Project Management Framework:
            
            The Project Management Framework provides a comprehensive REST API for managing projects, tasks, resources, and analytics.
            
            Authentication:
            All API endpoints require authentication using JWT tokens. Include the token in the Authorization header:
            Authorization: Bearer <your-jwt-token>
            
            Base URL: https://api.projectmanagement.com/v1
            
            Core Endpoints:
            
            Projects:
            - GET /projects - List all projects
            - POST /projects - Create new project
            - GET /projects/{id} - Get project details
            - PUT /projects/{id} - Update project
            - DELETE /projects/{id} - Delete project
            
            Tasks:
            - GET /projects/{id}/tasks - Get project tasks
            - POST /projects/{id}/tasks - Create new task
            - PUT /tasks/{id} - Update task
            - DELETE /tasks/{id} - Delete task
            
            Analytics:
            - GET /analytics/dashboard - Get dashboard metrics
            - GET /analytics/trends - Get trend analysis
            - GET /analytics/predictions - Get AI predictions
            
            Error Handling:
            The API returns standard HTTP status codes and detailed error messages in JSON format.
            
            Rate Limiting:
            API requests are limited to 1000 requests per hour per user.
            """,
            "metadata": {
                "doc_type": "API Documentation",
                "title": "Project Management API Reference",
                "version": "1.0",
                "category": "Technical Documentation",
                "author": "API Development Team",
                "created_at": "2024-02-05",
                "tags": ["API", "REST", "Documentation", "Projects", "Tasks"]
            }
        },
        {
            "content": """
            User Guide - Getting Started with Project Management:
            
            Welcome to the Project Management Framework! This guide will help you get started with managing your projects effectively.
            
            Getting Started:
            1. Login: Use your credentials to access the system
            2. Dashboard: View your project overview and key metrics
            3. Create Project: Start by creating your first project
            4. Add Tasks: Break down your project into manageable tasks
            5. Assign Resources: Allocate team members to tasks
            6. Track Progress: Monitor project status and milestones
            
            Key Features:
            - Project Templates: Use pre-built templates for common project types
            - Gantt Charts: Visualize project timelines and dependencies
            - Resource Management: Track team workload and availability
            - Risk Management: Identify and mitigate project risks
            - Reporting: Generate comprehensive project reports
            - AI Insights: Get intelligent recommendations and predictions
            
            Best Practices:
            1. Define clear project objectives and success criteria
            2. Break large projects into smaller, manageable phases
            3. Regularly update project status and communicate with stakeholders
            4. Use the AI-powered insights to optimize project performance
            5. Document lessons learned for future projects
            
            Support:
            For additional help, contact the support team or refer to the comprehensive documentation.
            """,
            "metadata": {
                "doc_type": "User Guide",
                "title": "Getting Started Guide",
                "version": "1.2",
                "category": "User Documentation",
                "author": "Product Team",
                "created_at": "2024-02-10",
                "tags": ["User Guide", "Getting Started", "Tutorial", "Best Practices"]
            }
        }
    ],
    "meetings": [
        {
            "content": """
            Project Kickoff Meeting - AI Analytics Platform:
            
            Meeting Date: February 15, 2024
            Duration: 2 hours
            Participants: Project Manager, Technical Lead, Business Analyst, Stakeholders
            
            Agenda:
            1. Project Overview and Objectives
            2. Scope Definition and Deliverables
            3. Timeline and Milestones
            4. Resource Allocation and Roles
            5. Risk Assessment and Mitigation
            6. Communication Plan and Reporting
            
            Key Decisions:
            - Project will be delivered in 3 phases over 6 months
            - Weekly status meetings every Friday at 2 PM
            - Monthly stakeholder reviews on the first Monday of each month
            - Use Agile methodology with 2-week sprints
            - Implement AI-powered analytics in Phase 2
            
            Action Items:
            1. Technical Lead: Complete technical architecture by March 1
            2. Business Analyst: Finalize requirements document by February 28
            3. Project Manager: Set up project tracking tools and communication channels
            4. Stakeholders: Provide feedback on initial requirements by February 25
            
            Next Meeting: February 22, 2024 - Sprint Planning Session
            """,
            "metadata": {
                "meeting_id": "M-001",
                "date": "2024-02-15",
                "participants": ["Project Manager", "Technical Lead", "Business Analyst", "Stakeholders"],
                "type": "Project Kickoff",
                "project_id": "AI-ANALYTICS",
                "duration": "2 hours",
                "status": "Completed"
            }
        },
        {
            "content": """
            Sprint Retrospective - Development Team:
            
            Meeting Date: February 28, 2024
            Duration: 1 hour
            Participants: Development Team, Scrum Master, Product Owner
            
            Sprint Review:
            - Completed 8 out of 10 planned user stories
            - Delivered core authentication and user management features
            - Identified performance bottlenecks in database queries
            - Successfully integrated AI model for project predictions
            
            What Went Well:
            - Strong collaboration between frontend and backend teams
            - Effective use of pair programming for complex features
            - Good communication with stakeholders during demos
            - Successful deployment to staging environment
            
            Areas for Improvement:
            - Need better test coverage for edge cases
            - Database optimization required for large datasets
            - Documentation could be more comprehensive
            - Code review process needs streamlining
            
            Action Items for Next Sprint:
            1. Implement database indexing for performance improvement
            2. Increase test coverage to 90%
            3. Create comprehensive API documentation
            4. Establish automated code review process
            
            Sprint Velocity: 32 story points (target: 30)
            """,
            "metadata": {
                "meeting_id": "M-002",
                "date": "2024-02-28",
                "participants": ["Development Team", "Scrum Master", "Product Owner"],
                "type": "Sprint Retrospective",
                "project_id": "AI-ANALYTICS",
                "duration": "1 hour",
                "status": "Completed"
            }
        }
    ],
    "knowledge_base": [
        {
            "content": """
            Project Management Methodologies Comparison:
            
            Different project management methodologies suit different types of projects and organizational cultures.
            
            Waterfall:
            - Sequential phases with clear deliverables
            - Best for: Well-defined requirements, stable scope
            - Pros: Clear structure, easy to manage, good documentation
            - Cons: Inflexible, late feedback, high risk of rework
            
            Agile:
            - Iterative development with frequent feedback
            - Best for: Dynamic requirements, innovation projects
            - Pros: Flexible, early feedback, high customer satisfaction
            - Cons: Requires experienced teams, can be chaotic
            
            Scrum:
            - Time-boxed iterations (sprints) with defined roles
            - Best for: Software development, complex projects
            - Pros: Clear roles, regular delivery, continuous improvement
            - Cons: Requires Scrum Master, can be rigid
            
            Kanban:
            - Visual workflow management with continuous delivery
            - Best for: Maintenance, support, continuous improvement
            - Pros: Flexible, visual, reduces waste
            - Cons: Less structure, requires discipline
            
            Hybrid Approaches:
            Many organizations combine methodologies based on project characteristics and organizational needs.
            """,
            "metadata": {
                "category": "Methodology",
                "tags": ["Project Management", "Methodologies", "Comparison", "Best Practices"],
                "author": "PMO Team",
                "version": "1.0",
                "created_at": "2024-02-12"
            }
        },
        {
            "content": """
            Stakeholder Management Best Practices:
            
            Effective stakeholder management is crucial for project success. Here are key strategies:
            
            Stakeholder Identification:
            1. Create stakeholder register with all individuals and groups affected by the project
            2. Categorize stakeholders by influence and interest levels
            3. Identify key decision makers and influencers
            4. Map stakeholder relationships and dependencies
            
            Communication Strategies:
            1. Tailor communication to each stakeholder's needs and preferences
            2. Establish regular communication schedules and formats
            3. Use appropriate communication channels (email, meetings, reports)
            4. Provide clear, concise, and relevant information
            
            Engagement Techniques:
            1. Involve stakeholders in project planning and decision making
            2. Address concerns and resistance proactively
            3. Build relationships through regular interaction
            4. Recognize and reward stakeholder contributions
            
            Managing Expectations:
            1. Set clear expectations from the beginning
            2. Communicate project constraints and limitations
            3. Provide regular updates on progress and changes
            4. Manage scope changes through proper change control
            
            Conflict Resolution:
            1. Address conflicts early before they escalate
            2. Use collaborative problem-solving approaches
            3. Focus on interests rather than positions
            4. Seek win-win solutions when possible
            """,
            "metadata": {
                "category": "Stakeholder Management",
                "tags": ["Stakeholders", "Communication", "Engagement", "Conflict Resolution"],
                "author": "Project Management Office",
                "version": "1.1",
                "created_at": "2024-02-18"
            }
        }
    ]
}

async def populate_rag_database():
    """Populate the RAG database with sample documents"""
    logger.info("🚀 Starting RAG database population...")
    
    try:
        # Get vector database instance
        vector_db = await get_vector_db()
        
        total_documents = 0
        
        # Populate each collection
        for collection_name, documents in SAMPLE_DOCUMENTS.items():
            logger.info(f"📚 Populating {collection_name} collection with {len(documents)} documents...")
            
            for doc_data in documents:
                try:
                    # Create document object
                    document = Document(
                        content=doc_data["content"].strip(),
                        metadata=doc_data["metadata"]
                    )
                    
                    # Add document to collection
                    await vector_db.add_document(collection_name, document)
                    total_documents += 1
                    
                    logger.info(f"✅ Added document: {doc_data['metadata'].get('name', 'Unnamed')}")
                    
                except Exception as e:
                    logger.error(f"❌ Error adding document to {collection_name}: {e}")
                    continue
        
        logger.info(f"🎉 Successfully populated RAG database with {total_documents} documents!")
        
        # Display collection statistics
        await display_collection_stats(vector_db)
        
    except Exception as e:
        logger.error(f"❌ Error populating RAG database: {e}")
        raise

async def display_collection_stats(vector_db):
    """Display statistics for all collections"""
    logger.info("📊 Collection Statistics:")
    
    try:
        stats = await vector_db.get_collection_stats()
        
        for collection_name, collection_stats in stats.items():
            logger.info(f"  📁 {collection_name}: {collection_stats['document_count']} documents")
            
    except Exception as e:
        logger.error(f"❌ Error getting collection stats: {e}")

async def main():
    """Main function"""
    logger.info("🔧 RAG Database Population Script")
    logger.info("=" * 50)
    
    try:
        await populate_rag_database()
        logger.info("✅ RAG database population completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ RAG database population failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
