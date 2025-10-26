"""add_get_model_full_function

Revision ID: 7ed6b3ca2bd8
Revises: 6e6e5fee3979
Create Date: 2025-10-25 14:32:20.164276

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ed6b3ca2bd8'
down_revision = '6e6e5fee3979'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the get_model_full function with model_type inside model and other_model
    op.execute("""
    CREATE OR REPLACE FUNCTION get_model_full(p_model_id bigint)
    RETURNS jsonb AS $$
    SELECT jsonb_build_object(
      'model', jsonb_build_object(
        'id', m.id,
        'title', m.title,
        'body', m.body,
        'created_at', m.created_at,
        'updated_at', m.updated_at,
        'model_type', jsonb_build_object(
          'base_model', jsonb_build_object(
            'id', mt.id,
            'name', mt.name,
            'description', mt.description
          ),
          'traits', COALESCE((
            SELECT jsonb_agg(
              jsonb_build_object(
                'id', tmt.id,
                'name', tmt.name,
                'description', tmt.description
              )
            )
            FROM trait_assignments ta
            JOIN model_types tmt ON ta.trait_type_id = tmt.id
            WHERE ta.model_id = m.id
          ), '[]'::jsonb)
        )
      ),
      'attributes', (
        SELECT jsonb_object_agg(ad.key,
          COALESCE(a.value_text,
                   a.value_number::text,
                   a.value_bool::text,
                   a.value_time::text)
        )
        FROM attributes a
        JOIN attribute_definitions ad
          ON a.attribute_definition_id = ad.id
        WHERE a.model_id = m.id
      ),
      'relations', COALESCE((
        SELECT jsonb_agg(
          jsonb_build_object(
            'relation_id', r.id,
            'relation_name', rt.relation_name,
            'direction', CASE WHEN r.from_id = p_model_id THEN 'outgoing' ELSE 'incoming' END,
            'other_model', jsonb_build_object(
              'id', m2.id,
              'title', m2.title,
              'body', m2.body,
              'created_at', m2.created_at,
              'updated_at', m2.updated_at,
              'model_type', jsonb_build_object(
                'base_model', jsonb_build_object(
                  'id', mt2.id,
                  'name', mt2.name,
                  'description', mt2.description
                ),
                'traits', COALESCE((
                  SELECT jsonb_agg(
                    jsonb_build_object(
                      'id', tmt2.id,
                      'name', tmt2.name,
                      'description', tmt2.description
                    )
                  )
                  FROM trait_assignments ta2
                  JOIN model_types tmt2 ON ta2.trait_type_id = tmt2.id
                  WHERE ta2.model_id = m2.id
                ), '[]'::jsonb)
              )
            ),
            'relation_attributes', (
              SELECT jsonb_object_agg(rad.key,
                COALESCE(ra.value_text,
                         ra.value_number::text,
                         ra.value_bool::text,
                         ra.value_time::text)
              )
              FROM relation_attributes ra
              JOIN relation_attribute_definitions rad
                ON ra.relation_attribute_definition_id = rad.id
              WHERE ra.relation_id = r.id
            )
          )
        )
        FROM relations r
        JOIN relationship_type rt ON rt.id = r.relationship_type_id
        JOIN models m2
          ON m2.id = CASE WHEN r.from_id = p_model_id THEN r.to_id ELSE r.from_id END
        JOIN model_types mt2 ON m2.model_type_id = mt2.id
        WHERE r.from_id = p_model_id OR r.to_id = p_model_id
      ), '[]'::jsonb)
    )
    FROM models m
    JOIN model_types mt ON m.model_type_id = mt.id
    WHERE m.id = p_model_id;
    $$ LANGUAGE sql STABLE;
    """)


def downgrade() -> None:
    # Drop the get_model_full function
    op.execute("DROP FUNCTION IF EXISTS get_model_full(bigint);")